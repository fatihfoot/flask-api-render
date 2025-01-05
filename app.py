from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# حالة اللعبة
game_state = {
    "is_open": False,
    "players": [],
    "team1": [],
    "team2": []
}

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    game_state["is_open"] = not game_state["is_open"]
    if game_state["is_open"]:
        game_state["team1"] = []
        game_state["team2"] = []
    return jsonify({"is_open": game_state["is_open"]})

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify({
        "is_open": game_state["is_open"],
        "players": game_state["players"]
    })

@app.route('/add_player', methods=['POST'])
def add_player():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return jsonify({"error": "User not identified"}), 403

    data = request.get_json()
    player_name = data.get("name")

    # تحقق إذا كان المستخدم قد أضاف بالفعل اسمًا
    if any(player["user_id"] == user_id for player in game_state["players"]):
        return jsonify({"error": "You have already added a name."}), 400

    # تحقق إذا كان الاسم موجودًا مسبقًا
    if any(player["name"] == player_name for player in game_state["players"]):
        return jsonify({"error": "Name already exists."}), 400

    game_state["players"].append({"name": player_name, "user_id": user_id})
    return jsonify({"message": "Player added successfully."})

@app.route('/distribute', methods=['POST'])
def distribute():
    players = [player["name"] for player in game_state["players"]]
    if len(players) < 2:
        return jsonify({"error": "Not enough players to distribute."}), 400

    # توزيع عشوائي مع الفلتر
    team1 = []
    team2 = []
    for player in players:
        if player == "ريشي":
            team1.append(player)
        elif player == "ياسين":
            team2.append(player)
        else:
            (team1 if len(team1) <= len(team2) else team2).append(player)

    game_state["team1"] = team1
    game_state["team2"] = team2
    return jsonify({"team1": team1, "team2": team2})

@app.route('/reset_players', methods=['POST'])
def reset_players():
    game_state["players"] = []
    return jsonify({"message": "All players have been reset."})

@app.route('/set_cookie', methods=['GET'])
def set_cookie():
    resp = make_response("Cookie set!")
    resp.set_cookie('user_id', str(random.randint(1000, 9999)))  # معرف فريد بسيط
    return resp

if __name__ == '__main__':
    app.run(debug=True)
