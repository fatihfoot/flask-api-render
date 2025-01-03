from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Connection String
MONGO_URI = "mongodb+srv://khalidfoot:Khalidd1233@fatih.zsrfd.mongodb.net/?retryWrites=true&w=majority&appName=fatih"
client = MongoClient(MONGO_URI)
db = client["test_db"]
collection = db["names"]

@app.route('/add-name', methods=['POST'])
def add_name():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    try:
        collection.insert_one({"name": name})
        return jsonify({"message": "Name added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
