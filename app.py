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

    client_id = request.remote_addr
    if client_id in added_players:
        return jsonify({"error": "You have already added a player"}), 403

    if len(state["players"]) >= MAX_PLAYERS:
        return jsonify({"error": "Max players reached"}), 403

    data = request.json
    player_name = data.get("name", "").strip()

    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    if player_name in state["players"]:
        return jsonify({"error": "Player name already exists"}), 400

    state["players"].append(player_name)
    added_players[client_id] = player_name

    return jsonify({"success": True, "players": state["players"]})

@app.route('/reset_players', methods=['POST'])
def reset_players():
    state["players"] = []
    added_players.clear()
    return jsonify({"success": True})

@app.route('/distribute', methods=['POST'])
def distribute_teams():
    if len(state["players"]) < 2:
        return jsonify({"error": "Not enough players to form teams"}), 400

    players = state["players"][:]
    random.shuffle(players)

    # شرط توزيع ريشي وياسين
    team1 = []
    team2 = []

    if "ريشي" in players and "ياسين" in players:
        team1.append("ريشي")
        team2.append("ياسين")
        players.remove("ريشي")
        players.remove("ياسين")

    for player in players:
        if len(team1) <= len(team2):
            team1.append(player)
        else:
            team2.append(player)

    return jsonify({"team1": team1, "team2": team2})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
