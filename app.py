from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

state = {
    "is_open": False,
    "players": []
}

@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)

@app.route("/toggle_open", methods=["POST"])
def toggle_open():
    state["is_open"] = not state["is_open"]
    return jsonify({"is_open": state["is_open"]})

@app.route("/add_player", methods=["POST"])
def add_player():
    if not state["is_open"]:
        return jsonify({"error": "Session is closed"}), 403
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if name in state["players"]:
        return jsonify({"error": "Player already added"}), 400
    if len(state["players"]) >= 12:
        return jsonify({"error": "Maximum players reached"}), 403
    state["players"].append(name)
    return jsonify({"success": True})

@app.route("/reset_players", methods=["POST"])
def reset_players():
    state["players"] = []
    return jsonify({"success": True})

@app.route("/distribute", methods=["POST"])
def distribute():
    players = state["players"]
    if len(players) < 2:
        return jsonify({"error": "Not enough players"}), 400
    team1 = []
    team2 = []

    for player in players:
        if "ريشي" in team1 and "ياسين" == player:
            team2.append(player)
        elif "ياسين" in team1 and "ريشي" == player:
            team2.append(player)
        elif len(team1) <= len(team2):
            team1.append(player)
        else:
            team2.append(player)

    return jsonify({"team1": team1, "team2": team2})

if __name__ == "__main__":
    app.run(debug=True)
