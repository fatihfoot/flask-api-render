from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
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

# Route to register a user
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    city = data.get('city')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not first_name or not last_name or not email or not phone or not city or not password or not confirm_password:
        return jsonify({"error": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Hash password
    hashed_password = generate_password_hash(password)
    
    # Save the user with status "Pending"
    collection.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "city": city,
        "password": hashed_password,
        "status": "Pending",  # Status is set to 'Pending'
    })

    return jsonify({"message": "User registered successfully. Await admin approval."}), 201

# Route for admin to approve user
@app.route('/approve_user', methods=['POST'])
def approve_user():
    data = request.json
    user_id = data.get('user_id')

    # Find the user and update their status to "Approved"
    user = collection.find_one({"_id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    collection.update_one({"_id": user["_id"]}, {"$set": {"status": "Approved"}})
    
    return jsonify({"message": "User approved successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
