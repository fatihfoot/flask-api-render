from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف جدول اللاعبين
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)

# تعريف جدول حالة اللعبة
class GameState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_open = db.Column(db.Boolean, default=False)
    team1 = db.Column(db.String, default="")
    team2 = db.Column(db.String, default="")

# تهيئة قاعدة البيانات عند بدء الخادم
def init_database():
    # إنشاء الجداول
    db.create_all()

    # التحقق من وجود الأعمدة "team1" و "team2" في جدول "game_state"
    with db.engine.connect() as connection:
        if not column_exists("game_state", "team1"):
            connection.execute(text('ALTER TABLE game_state ADD COLUMN "team1" TEXT DEFAULT ""'))
        if not column_exists("game_state", "team2"):
            connection.execute(text('ALTER TABLE game_state ADD COLUMN "team2" TEXT DEFAULT ""'))

    # إضافة صف افتراضي إذا لم يكن موجودًا
    state = GameState.query.first()
    if not state:
        db.session.add(GameState(is_open=False))
        db.session.commit()


    # التحقق من وجود الأعمدة "team1" و "team2" في جدول "game_state"
    with db.engine.connect() as connection:
        if not column_exists("game_state", "team1"):
            connection.execute(text('ALTER TABLE game_state ADD COLUMN "team1" TEXT DEFAULT ""'))
        if not column_exists("game_state", "team2"):
            connection.execute(text('ALTER TABLE game_state ADD COLUMN "team2" TEXT DEFAULT ""'))

def column_exists(table_name, column_name):
    """التأكد من وجود عمود معين في جدول"""
    query = text(f"PRAGMA table_info({table_name});")
    with db.engine.connect() as connection:
        result = connection.execute(query).fetchall()
        return any(row[1] == column_name for row in result)

# مسار لتغيير حالة اللعبة
@app.route('/toggle_open', methods=['POST'])
def toggle_open():
    state = GameState.query.first()
    state.is_open = not state.is_open
    db.session.commit()
    return jsonify({'is_open': state.is_open})

# مسار لإضافة لاعب جديد
@app.route('/add_player', methods=['POST'])
def add_player():
    state = GameState.query.first()
    if not state.is_open:
        return jsonify({'error': 'Game is closed'}), 400

    players = Player.query.all()
    if len(players) >= 4:
        return jsonify({'error': 'Maximum players reached'}), 400

    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    if Player.query.filter_by(name=name).first():
        return jsonify({'error': 'Player already exists'}), 400

    player_order = len(players) + 1
    player = Player(name=name, order=player_order)
    db.session.add(player)
    db.session.commit()
    return jsonify({'message': f'Player {name} added successfully'})

# مسار للحصول على حالة اللعبة وعدد اللاعبين
@app.route('/state', methods=['GET'])
def get_state():
    state = GameState.query.first()
    players = Player.query.order_by(Player.order).all()
    return jsonify({
        'is_open': state.is_open,
        'players': [{'id': p.id, 'name': p.name} for p in players],
        'player_count': len(players),
        'team1': state.team1.split(',') if state.team1 else [],
        'team2': state.team2.split(',') if state.team2 else []
    })

# مسار لتوزيع اللاعبين
@app.route('/distribute', methods=['POST'])
def distribute_players():
    players = Player.query.order_by(Player.order).all()
    if len(players) != 4:
        return jsonify({'error': 'Must have exactly 4 players to distribute'}), 400

    # توزيع عشوائي
    random.shuffle(players)
    team1 = [p.name for p in players[:2]]
    team2 = [p.name for p in players[2:]]

    # حفظ التوزيع في قاعدة البيانات
    state = GameState.query.first()
    state.team1 = ",".join(team1)  # تحويل قائمة الأسماء إلى سلسلة نصوص
    state.team2 = ",".join(team2)
    db.session.commit()

    return jsonify({'team1': team1, 'team2': team2})
@app.route('/reset_players', methods=['POST'])
def reset_players():
    """حذف جميع اللاعبين"""
    db.session.query(Player).delete()  # حذف جميع السجلات من جدول اللاعبين
    state = GameState.query.first()
    state.team1 = ""
    state.team2 = ""
    db.session.commit()
    return jsonify({'message': 'تم حذف جميع اللاعبين بنجاح.'})

# مسار لإعادة تعيين اللعبة
@app.route('/reset', methods=['POST'])
def reset_game():
    db.session.query(Player).delete()
    state = GameState.query.first()
    state.is_open = False
    state.team1 = ""
    state.team2 = ""
    db.session.commit()
    return jsonify({'message': 'Game has been reset'})

if __name__ == '__main__':
    with app.app_context():
        init_database()
    app.run(debug=True)
