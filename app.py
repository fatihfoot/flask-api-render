from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import json

# MongoDB setup
client = MongoClient(os.environ["MONGODB_URI"])
db = client["flet_database"]
users_collection = db["users"]

# Flask app setup
app = Flask(__name__)

# Route for registering new users
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    city = data.get('city')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([first_name, last_name, email, phone, city, password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400
    
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    hashed_password = generate_password_hash(password)
    created_at = datetime.utcnow()
    remaining_time = timedelta(days=30)  # فرضًا المدة 30 يومًا من تاريخ التسجيل

    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "city": city,
        "password": hashed_password,
        "created_at": created_at,
        "remaining_time": remaining_time
    }

    users_collection.insert_one(user_data)

    return jsonify({"message": "User registered successfully!"}), 201

# Route for login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid credentials"}), 400

    return jsonify({"message": "Login successful!"}), 200

# Admin route to view all users and manage them
@app.route('/admin/users', methods=['GET'])
def get_users():
    users = users_collection.find()
    user_list = []

    for user in users:
        user_list.append({
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "phone": user["phone"],
            "city": user["city"],
            "created_at": user["created_at"].strftime('%Y-%m-%d %H:%M:%S'),
            "remaining_time": str(user["remaining_time"])
        })
    
    return jsonify(user_list), 200

# Admin route to update the remaining time of a user
@app.route('/admin/update_time', methods=['POST'])
def update_time():
    data = request.json
    email = data.get('email')
    new_time = int(data.get('remaining_time'))  # in days

    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update the remaining time
    new_remaining_time = timedelta(days=new_time)
    users_collection.update_one({"email": email}, {"$set": {"remaining_time": new_remaining_time}})
    
    return jsonify({"message": "User time updated successfully!"}), 200

# Admin route to delete a user
@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    data = request.json
    email = data.get('email')

    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "User not found"}), 404

    users_collection.delete_one({"email": email})

    return jsonify({"message": "User deleted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
