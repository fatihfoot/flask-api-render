from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os
from cryptography.fernet import Fernet

# Load encryption key for MongoDB URI
key = os.environ.get("ENCRYPTION_KEY").encode()
cipher = Fernet(key)

# Decrypt MongoDB URI
encrypted_uri = os.environ.get("ENCRYPTED_MONGODB_URI").encode()
MONGODB_URI = cipher.decrypt(encrypted_uri).decode()

# Flask app
app = Flask(__name__)

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client["flet_database"]
collection = db["users"]

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    
    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400
    
    # Hash password
    hashed_password = generate_password_hash(password)
    
    # Save to MongoDB
    collection.insert_one({"name": name, "password": hashed_password})
    return jsonify({"message": "User added successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
