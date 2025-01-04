from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import os
from cryptography.fernet import Fernet

# Load environment variables and encryption key
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
ENCRYPTED_MONGODB_URI = os.environ.get("ENCRYPTED_MONGODB_URI")

if not ENCRYPTION_KEY or not ENCRYPTED_MONGODB_URI:
    raise ValueError("Missing required environment variables: ENCRYPTION_KEY or ENCRYPTED_MONGODB_URI")

# Load encryption key for MongoDB URI
key = ENCRYPTION_KEY.encode()
cipher = Fernet(key)

# Decrypt MongoDB URI
encrypted_uri = ENCRYPTED_MONGODB_URI.encode()
MONGODB_URI = cipher.decrypt(encrypted_uri).decode()

# Flask app setup
app = Flask(__name__)

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client["flet_database"]
collection = db["users"]

# General error handler
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled Exception: {e}")
    return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

# Route to register a user
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        print("Received data for registration:", data)

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Retrieve data from request
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        city = data.get('city')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check for missing fields
        if not all([first_name, last_name, email, phone, city, password, confirm_password]):
            return jsonify({"error": "All fields are required"}), 400

        # Check if passwords match
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Check if email already exists
        if collection.find_one({"email": email}):
            return jsonify({"error": "Email already exists"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save the user to the database
        user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "city": city,
            "password": hashed_password,
            "status": "Pending"
        }

        result = collection.insert_one(user)
        print("User added to database with ID:", result.inserted_id)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Route to login a user
@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        print(f"Received login request: {data}")

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # البحث عن المستخدم
        user = collection.find_one({"email": email})
        print(f"User found: {user}")

        if not user:
            print("Error: User not found")
            return jsonify({"error": "User not found"}), 404

        # تحقق من كلمة المرور أولاً
        print(f"Entered password: {password}")
        print(f"Stored hashed password: {user['password']}")
        if not check_password_hash(user["password"], password):
            print("Error: Invalid password")
            return jsonify({"error": "Invalid password"}), 401

        # تحقق من حالة المستخدم
        if user.get("status") != "Approved":
            print(f"Error: User status is {user.get('status')}")
            return jsonify({"error": "Account not approved yet"}), 403

        # تسجيل الدخول ناجح
        print("Login successful")
        return jsonify({
            "message": "Login successful",
            "status": user["status"]
        }), 200

    except Exception as e:
        print(f"Unhandled Exception during login: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
# Route for admin to approve user
@app.route('/approve_user', methods=['POST'])
def approve_user():
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        user_object_id = ObjectId(user_id)
        user = collection.find_one({"_id": user_object_id})
        if not user:
            return jsonify({"error": "User not found"}), 404

        collection.update_one({"_id": user_object_id}, {"$set": {"status": "Approved"}})
        print(f"User {user_id} approved successfully")
        return jsonify({"message": "User approved successfully"}), 200

    except Exception as e:
        print(f"Error during approval: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Route to check pending users
@app.route('/pending_users', methods=['GET'])
def get_pending_users():
    try:
        pending_users = list(collection.find({"status": "Pending"}))
        for user in pending_users:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string for JSON
        return jsonify({"users": pending_users}), 200
    except Exception as e:
        print(f"Error retrieving pending users: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Route to check if email exists
@app.route('/check_email/<email>', methods=['GET'])
def check_email(email):
    try:
        user = collection.find_one({"email": email})
        return jsonify({"exists": bool(user)}), 200
    except Exception as e:
        print(f"Error checking email existence: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)
