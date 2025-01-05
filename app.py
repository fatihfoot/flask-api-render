from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

state = {
    "is_open": False,
    "players": [],
}

MAX_PLAYERS = 12
added_players = {}

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(state)

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    state["is_open"] = not state["is_open"]
    return jsonify({"is_open": state["is_open"]})

@app.route('/add_player', methods=['POST'])
def add_player():
    if not state["is_open"]:
        return jsonify({"error": "Session is closed"}), 403

    data = request.json
    client_uuid = data.get("uuid", None)

    if not client_uuid:
        return jsonify({"error": "Missing UUID"}), 400

    if client_uuid in added_players:
        return jsonify({"error": "لقد قمت بالفعل بضافة الاعب"}), 403

    if len(state["players"]) >= MAX_PLAYERS:
        return jsonify({"error": "تم الوصول للحد الاقصى من لاعبين حظ موفق في المرة القادمة"}), 403

    player_name = data.get("name", "").strip()

    if not player_name:
        return jsonify({"error": "اسم لاعب مطلوب"}), 400

    state["players"].append({"name": player_name, "uuid": client_uuid})
    added_players[client_uuid] = player_name

    return jsonify({"success": True, "players": state["players"]})

@app.route('/reset_players', methods=['POST'])
def reset_players():
    state["players"] = []
    added_players.clear()
    return jsonify({"success": True})

@app.route('/distribute', methods=['POST'])
def distribute_teams():
    if len(state["players"]) < 2:
        return jsonify({"error": "لايمكن تقسيم لاعب واحد"}), 400

    players = state["players"][:]
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
