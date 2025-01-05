from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# تخزين اللاعبين و UUIDs والجلسة الحالية
players = []  # قائمة بأسماء اللاعبين
uuid_to_player = {}  # خريطة من UUID إلى اسم اللاعب والجلسة
current_session_id = str(uuid.uuid4())  # معرف الجلسة الحالي
MAX_PLAYERS = 12  # الحد الأقصى لعدد اللاعبين
is_open = False  # حالة الأزرار (مغلقة أو مفتوحة)

@app.route('/state', methods=['GET'])
def get_state():
    """إرجاع حالة اللعبة."""
    return jsonify({
        "is_open": is_open,
        "players": players
    })

@app.route('/add_player', methods=['POST'])
def add_player():
    """إضافة لاعب جديد."""
    global players, uuid_to_player

    data = request.get_json()
    name = data.get("name")
    user_uuid = data.get("uuid")

    # تحقق من صحة البيانات
    if not name or not user_uuid:
        return jsonify({"error": "اسم اللاعب أو UUID مفقود."}), 400

    # تحقق من حالة الجلسة
    if not is_open:
        return jsonify({"error": "الأزرار مغلقة حاليًا."}), 403

    # تحقق من الحد الأقصى للاعبين
    if len(players) >= MAX_PLAYERS:
        return jsonify({"error": "تم الوصول إلى الحد الأقصى لعدد اللاعبين."}), 403

    # تحقق من أن المستخدم لم يسجل بالفعل في الجلسة الحالية
    if user_uuid in uuid_to_player and uuid_to_player[user_uuid] == current_session_id:
        return jsonify({"error": "لقد قمت بإضافة اسم مسبقًا في هذه الجلسة."}), 403

    # إضافة اللاعب
    players.append(name)
    uuid_to_player[user_uuid] = current_session_id
    return jsonify({"message": f"تمت إضافة {name} بنجاح."}), 200

@app.route('/reset_players', methods=['POST'])
def reset_players():
    """إعادة تعيين اللاعبين وبدء جلسة جديدة."""
    global players, uuid_to_player, current_session_id, is_open
    players = []
    uuid_to_player = {}
    current_session_id = str(uuid.uuid4())  # إنشاء معرف جلسة جديد
    is_open = False  # إغلاق الأزرار بعد إعادة التعيين
    return jsonify({"message": "تمت إعادة تعيين جميع اللاعبين وبدء جلسة جديدة."}), 200

@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    """فتح/إغلاق أزرار المستخدمين."""
    global is_open
    is_open = not is_open
    return jsonify({"is_open": is_open})

if __name__ == '__main__':
    app.run(debug=True)
