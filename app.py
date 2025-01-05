from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# البيانات في الذاكرة
state = {
    "is_open": False,
    "players": []
}

@app.route('/state', methods=['GET'])
def get_state():
    """إرجاع حالة اللعبة."""
    return jsonify(state)

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    """تبديل حالة الأزرار بين الفتح والإغلاق."""
    state["is_open"] = not state["is_open"]
    return jsonify({"is_open": state["is_open"]})

@app.route('/add_player', methods=['POST'])
def add_player():
    """إضافة لاعب جديد إلى القائمة."""
    data = request.get_json()
    player_name = data.get("name")

    if not player_name:
        return jsonify({"error": "الاسم مطلوب."}), 400

    if player_name in state["players"]:
        return jsonify({"error": "اللاعب موجود بالفعل."}), 400

    if len(state["players"]) >= 12:
        return jsonify({"error": "تم الوصول إلى الحد الأقصى لعدد اللاعبين."}), 400

    state["players"].append(player_name)
    return jsonify({"message": "تمت إضافة اللاعب بنجاح."}), 200

@app.route('/reset_players', methods=['POST'])
def reset_players():
    """إعادة تعيين قائمة اللاعبين."""
    state["players"] = []
    return jsonify({"message": "تمت إعادة تعيين اللاعبين."}), 200

@app.route('/distribute', methods=['POST'])
def distribute():
    """توزيع اللاعبين إلى فريقين."""
    if len(state["players"]) < 2:
        return jsonify({"error": "عدد اللاعبين غير كافٍ للتوزيع."}), 400

    random.shuffle(state["players"])

    team1 = []
    team2 = []

    for player in state["players"]:
        if "ريشي" in team1 and player == "ياسين":
            team2.append(player)
        elif "ياسين" in team1 and player == "ريشي":
            team2.append(player)
        elif "ريشي" in team2 and player == "ياسين":
            team1.append(player)
        elif "ياسين" in team2 and player == "ريشي":
            team1.append(player)
        else:
            if len(team1) <= len(team2):
                team1.append(player)
            else:
                team2.append(player)

    return jsonify({"team1": team1, "team2": team2}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
