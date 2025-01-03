from flask import Flask, request, jsonify
from pymongo import MongoClient
from cryptography.fernet import Fernet

app = Flask(__name__)

# MongoDB Connection String
MONGO_URI = "mongodb+srv://khalidfoot:Khalidd1233@fatih.zsrfd.mongodb.net/?retryWrites=true&w=majority&appName=fatih"
client = MongoClient(MONGO_URI)
db = client["test_db"]
collection = db["names"]

# مفتاح التشفير نفسه الذي استخدمناه في الجهة العميلة
key = b"your-secret-key-here"  # يجب أن يتطابق مع المفتاح في الجهة العميلة
cipher_suite = Fernet(key)

@app.route('/add-name', methods=['POST'])
def add_name():
    data = request.json
    encrypted_name = data.get('name')

    if not encrypted_name:
        return jsonify({"error": "Name is required"}), 400

    try:
        # فك التشفير
        name = cipher_suite.decrypt(encrypted_name.encode()).decode()

        # تخزين الاسم المفكوك في MongoDB
        collection.insert_one({"name": name})
        return jsonify({"message": "Name added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
