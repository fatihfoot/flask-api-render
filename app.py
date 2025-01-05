from flask import Flask, request, jsonify

app = Flask(__name__)

# تخزين اللاعبين و UUIDs
players = []  # قائمة بأسماء اللاعبين
uuid_to_player = {}  # خريطة من UUID إلى اسم اللاعب

MAX_PLAYERS = 12  # الحد الأقصى لعدد اللاعبين

@app.route('/state', methods=['GET'])
def get_state():
    """إرجاع حالة اللعبة."""
    return jsonify({
        "is_open": True,  # الأزرار مفتوحة دائمًا (يمكنك التحكم من واجهة الأدمين)
        "players": players
    })

@app.route('/add_player', methods=['POST'])
def add_player():
    """إضافة لاعب جديد."""
    data = request.get_json()
    name = data.get("name")
    user_uuid = data.get("uuid")

    # تحقق من صحة البيانات
    if not name or not user_uuid:
        return jsonify({"error": "اسم اللاعب أو UUID مفقود."}), 400

    # تحقق من الحد الأقصى للاعبين
    if len(players) >= MAX_PLAYERS:
        return jsonify({"error": "تم الوصول إلى الحد الأقصى لعدد اللاعبين."}), 403

    # تحقق من أن المستخدم لم يسجل بالفعل
    if user_uuid in uuid_to_player:
        return jsonify({"error": "لقد قمت بإضافة اسم مسبقًا."}), 403

    # إضافة اللاعب
    players.append(name)
    uuid_to_player[user_uuid] = name
    return jsonify({"message": f"تمت إضافة {name} بنجاح."}), 200

@app.route('/reset_players', methods=['POST'])
def reset_players():
    """إعادة تعيين اللاعبين."""
    global players, uuid_to_player
    players = []
    uuid_to_player = {}
    return jsonify({"message": "تمت إعادة تعيين جميع اللاعبين."}), 200

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    """تبديل حالة الأزرار (مثال فقط، الحالة ثابتة هنا)."""
    return jsonify({"is_open": True})  # الأزرار تبقى مفتوحة

if __name__ == '__main__':
    app.run(debug=True)
