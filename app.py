from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import random

app = Flask(__name__)
CORS(app)

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://khalidfoot:Khalidd1233@fatih.zsrfd.mongodb.net/?retryWrites=true&w=majority&appName=fatih"
client = MongoClient(MONGO_URI)
db = client["team_game"]  # Database name
players_collection = db["players"]  # Collection for players
state_collection = db["state"]  # Collection for game state

MAX_PLAYERS = 12

# Initialize state from MongoDB
state_doc = state_collection.find_one()
if state_doc:
    state = {"is_open": state_doc.get("is_open", False)}
else:
    state = {"is_open": False}

@app.route('/state', methods=['GET'])
def get_state():
    """Retrieve the current state."""
    players = list(players_collection.find({}, {"_id": 0}))  # Get players without MongoDB IDs
    return jsonify({"is_open": state["is_open"], "players": players})

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    """Toggle session open/closed."""
    state["is_open"] = not state["is_open"]
    state_collection.update_one({}, {"$set": {"is_open": state["is_open"]}}, upsert=True)
    return jsonify({"is_open": state["is_open"]})

@app.route('/add_player', methods=['POST'])
def add_player():
    """Add a new player to the session."""
    if not state["is_open"]:
        return jsonify({"error": "Session is closed"}), 403

    data = request.json
    client_uuid = data.get("uuid", None)

    if not client_uuid:
        return jsonify({"error": "Missing UUID"}), 400

    if players_collection.find_one({"uuid": client_uuid}):
        return jsonify({"error": "لقد قمت بالفعل بضافة الاعب"}), 403

    if players_collection.count_documents({}) >= MAX_PLAYERS:
        return jsonify({"error": "تم الوصول للحد الاقصى من لاعبين حظ موفق في المرة القادمة"}), 403

    player_name = data.get("name", "").strip()
    if not player_name:
        return jsonify({"error": "اسم لاعب مطلوب"}), 400

    player = {"name": player_name, "uuid": client_uuid}
    players_collection.insert_one(player)
    return jsonify({"success": True, "players": list(players_collection.find({}, {"_id": 0}))})

@app.route('/reset_players', methods=['POST'])
def reset_players():
    """Reset all players."""
    players_collection.delete_many({})
    return jsonify({"success": True})

@app.route('/distribute', methods=['POST'])
def distribute_teams():
    """Distribute players into two teams."""
    players = list(players_collection.find({}, {"_id": 0}))

    if len(players) < 2:
        return jsonify({"error": "لايمكن تقسيم لاعب واحد"}), 400

    random.shuffle(players)
    team1, team2 = [], []
    for player in players:
        if player["name"] == "ياسين" and any(p["name"] == "ريشي" for p in players):
            if "ريشي" not in [p["name"] for p in team1]:
                team1.append(player)
            else:
                team2.append(player)
        elif player["name"] == "ريشي" and any(p["name"] == "ياسين" for p in players):
            if "ياسين" not in [p["name"] for p in team2]:
                team2.append(player)
            else:
                team1.append(player)
        elif len(team1) <= len(team2):
            team1.append(player)
        else:
            team2.append(player)

    return jsonify({"team1": [p["name"] for p in team1], "team2": [p["name"] for p in team2]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
