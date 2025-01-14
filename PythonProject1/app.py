from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)
Migrate(app, db)

# модель для хранения задачи
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)

# презентер для задачи
def present_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "is_done": task.is_done
    }

# получаем все задачи
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return [present_task(task) for task in tasks]

# добавляем новую задачу
@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()

    # если нет названия - возвращаем ошибку
    if not data.get('title'):
        return jsonify({'error': 'no title'}), 400

    task = Task(title=data['title'])
    db.session.add(task)
    db.session.commit()

    return present_task(task)

# при запросе главной страницы возвращаем html файл с фронтендом как файл (без шаблонизатора)
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)