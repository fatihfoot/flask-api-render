from flask import Flask, request, jsonify
from pymongo import MongoClient
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# تحميل المفتاح السري من البيئة (يجب إضافته في Render)
SECRET_KEY = os.getenv('SECRET_KEY')
MONGO_URI = os.getenv('MONGO_URI')

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is required")

cipher_suite = Fernet(SECRET_KEY)

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["test_db"]
collection = db["names"]

@app.route('/add-name', methods=['POST'])
def add_name():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    # تشفير الاسم قبل حفظه
    encrypted_name = cipher_suite.encrypt(name.encode())

    try:
        collection.insert_one({"name": encrypted_name})
        return jsonify({"message": "Name added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
