from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# حالة اللعبة
game_state = {
    "is_open": False,
    "players": [],  # قائمة اللاعبين {name: str, user_id: str}
    "team1": [],
    "team2": []
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

@app.route('/reset_players', methods=['POST'])
def reset_players():
    """إعادة تعيين قائمة اللاعبين"""
    game_state["players"] = []
    game_state["team1"] = []
    game_state["team2"] = []
    return jsonify({"success": True})

@app.route('/add_player', methods=['POST'])
def add_player():
    """إضافة لاعب جديد"""
    data = request.get_json()
    name = data.get('name')
    user_id = data.get('user_id')

    if not name or not user_id:
        return jsonify({"error": "اسم اللاعب أو معرف المستخدم غير متوفر"}), 400

    # تحقق إذا كان المستخدم قد أضاف اسمه بالفعل
    if any(player['user_id'] == user_id for player in game_state["players"]):
        return jsonify({"error": "لقد قمت بإضافة اسمك بالفعل"}), 403

    # تحقق من عدد اللاعبين (حد أقصى 12)
    if len(game_state["players"]) >= 12:
        return jsonify({"error": "تم الوصول إلى الحد الأقصى لعدد اللاعبين"}), 403

    # إضافة اللاعب
    game_state["players"].append({"name": name, "user_id": user_id})
    return jsonify({"success": True}), 200

@app.route('/distribute', methods=['POST'])
def distribute():
    """توزيع اللاعبين عشوائيًا"""
    players = [player["name"] for player in game_state["players"]]

    if len(players) < 2:
        return jsonify({"error": "عدد اللاعبين غير كافٍ للتوزيع"}), 400

    random.shuffle(players)

    # توزيع اللاعبين مع مراعاة "ريشي" و"ياسين"
    team1, team2 = [], []
    for player in players:
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

    game_state["team1"] = team1
    game_state["team2"] = team2

    return jsonify({"team1": team1, "team2": team2})

if __name__ == '__main__':
    app.run(debug=True)
