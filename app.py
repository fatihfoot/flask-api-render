import os
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# استرجاع المفتاح السري من المتغير البيئي
SECRET_KEY = os.getenv('SECRET_KEY')

# إنشاء كائن Fernet باستخدام المفتاح السري
cipher_suite = Fernet(SECRET_KEY)

# MongoDB Connection String
MONGO_URI = "mongodb+srv://your-mongo-uri"
client = MongoClient(MONGO_URI)
db = client["test_db"]
collection = db["names"]

@app.route('/add-name', methods=['POST'])
def add_name():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    # تشفير الاسم قبل تخزينه
    encrypted_name = cipher_suite.encrypt(name.encode())

    try:
        # تخزين الاسم المشفر في MongoDB
        collection.insert_one({"name": encrypted_name})
        return jsonify({"message": "Name added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
