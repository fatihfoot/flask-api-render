from flask import Flask, request, jsonify

app = Flask(__name__)

# الحالة والبيانات في الذاكرة
game_state = {
    "is_open": False,
    "team1": [],
    "team2": [],
    "players": []
}

@app.route('/state', methods=['GET'])
def get_state():
    """إرجاع حالة اللعبة"""
    return jsonify({
        "is_open": game_state["is_open"],
        "players": game_state["players"],
        "team1": game_state["team1"],
        "team2": game_state["team2"]
    })

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    """فتح/إغلاق الأزرار"""
    game_state["is_open"] = not game_state["is_open"]
    return jsonify({"is_open": game_state["is_open"]})

@app.route('/add_player', methods=['POST'])
def add_player():
    """إضافة لاعب"""
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "الاسم مطلوب"}), 400

    if name in game_state["players"]:
        return jsonify({"error": "اللاعب موجود بالفعل"}), 400

    game_state["players"].append(name)
    return jsonify({"message": f"تم إضافة {name} بنجاح."}), 200

@app.route('/reset_players', methods=['POST'])
def reset_players():
    """مسح جميع اللاعبين"""
    game_state["players"] = []
    game_state["team1"] = []
    game_state["team2"] = []
    return jsonify({"message": "تم مسح جميع اللاعبين بنجاح."})

if __name__ == '__main__':
    app.run(debug=True)
