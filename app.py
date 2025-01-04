from flask import Flask, request, jsonify
from pymongo import MongoClient
import random
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
encrypted_uri = ENCRYPTED_MONGODB_URI.encode()
MONGODB_URI = cipher.decrypt(encrypted_uri).decode()

# Flask app setup
app = Flask(__name__)

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client["flet_database"]
teams_collection = db["teams"]

# General error handler
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled Exception: {e}")
    return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

# Route for admin to add players and create teams
@app.route('/add_player', methods=['POST'])
def add_player():
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({"error": "Player name is required"}), 400

        # Add player to the collection
        teams_collection.insert_one({"name": name, "team": None})
        print(f"Player {name} added successfully")

        # Check if we have 4 players to create teams
        players = list(teams_collection.find({"team": None}))
        if len(players) == 4:
            random.shuffle(players)
            team_a = players[:2]
            team_b = players[2:]

            # Assign players to teams
            for player in team_a:
                teams_collection.update_one({"_id": player["_id"]}, {"$set": {"team": "A"}})
            for player in team_b:
                teams_collection.update_one({"_id": player["_id"]}, {"$set": {"team": "B"}})

            return jsonify({
                "message": "Teams created successfully",
                "team_a": [player["name"] for player in team_a],
                "team_b": [player["name"] for player in team_b],
            }), 200

        return jsonify({"message": "Player added successfully, waiting for more players"}), 200

    except Exception as e:
        print(f"Error during adding player: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Route to view teams
@app.route('/view_teams', methods=['GET'])
def view_teams():
    try:
        team_a = list(teams_collection.find({"team": "A"}))
        team_b = list(teams_collection.find({"team": "B"}))

        return jsonify({
            "team_a": [player["name"] for player in team_a],
            "team_b": [player["name"] for player in team_b],
        }), 200

    except Exception as e:
        print(f"Error retrieving teams: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)
