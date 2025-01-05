from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# المتغيرات العامة
state = {
    "is_open": False,
    "players": [],
}

MAX_PLAYERS = 12

# تتبع المستخدمين المضافين
added_players = set()


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

    client_ip = request.remote_addr  # تحديد هوية المستخدم عبر IP
    if client_ip in added_players:
        return jsonify({"error": "You have already added a player"}), 403

    if len(state["players"]) >= MAX_PLAYERS:
        return jsonify({"error": "Max players reached"}), 403

    data = request.json
    player_name = data.get("name", "").strip()

    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    # إضافة اللاعب وتسجيل IP
    state["players"].append(player_name)
    added_players.add(client_ip)

    return jsonify({"success": True, "players": state["players"]})


@app.route('/reset_players', methods=['POST'])
def reset_players():
    state["players"] = []
    added_players.clear()  # إعادة تعيين قائمة اللاعبين المضافين
    return jsonify({"success": True})


@app.route('/check_cookie', methods=['GET'])
def check_cookie():
    client_ip = request.remote_addr
    return jsonify({"user_added": client_ip in added_players})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
