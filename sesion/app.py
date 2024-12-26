from flask import Flask, request, jsonify, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import random
import jwt
import time

from functools import wraps

from sqlalchemy.testing.provision import register

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# секретный ключ, которым мы шифруем данные
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
app.secret_key = 'jrfasefasefgj'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    last_generation = db.Column(db.Integer, nullable=True)

class Term(db.Model):
    __tablename__= 'term'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(80), nullable=False)

def requires_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # получаем токен из заголовков запроса
        token = session.get('token')
        alert = ''
        # если токена нет - возвращаем ошибку
        if not token:
            alert = 'Missing token'

        # расшифровываем токен и получаем его содержимое
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            alert = 'Invalid token'

        # получаем id пользователя и время генерации из токена
        user_id = payload.get('user_id')
        created_at = payload.get('created_at')

        # если чего-то нет - возвращаем ошибку
        if not user_id or not created_at:
            alert = 'Invalid token'

        # находим пользователя, если его нет - возвращаем ошибку
        user = User.query.filter_by(id=user_id).first()
        if not user:
            alert = 'User not found'

        # если с момента генерации прошло больше суток, просим войти заного
        if created_at + 60 * 60 * 24 < int(time.time()):
            alert = 'Token expired'

        # передаем в целевой эндпоинт пользователя и параметры пути
        return func(user, alert, *args, **kwargs)

    return wrapper

@app.route('/')
def index():
    return redirect('/register')
@app.route('/register', methods=['POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('log.html', alert='Missing data')

    if User.query.filter_by(login=login).first():
        return render_template('log.html', alert='User already exists')

    # заменяем пароль на хэш пароля
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(login=login, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    session['token'] = jwt.encode({'user_id': user.id, 'created_at': int(time.time())}, app.config['SECRET_KEY'],
                                  algorithm='HS256')
    return redirect('/terms')

@app.route('/login', methods=['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('log.html', alert='Missing data')

    # ищем пользователя в базе и проверяем хэш пароля
    user = User.query.filter_by(login=login).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return render_template('log.html', alert='Invalid credentials')

    # генерируем токен с id пользователя и временем создания
    session['token'] = jwt.encode({'user_id': user.id, 'created_at': int(time.time())}, app.config['SECRET_KEY'],
                       algorithm='HS256')

    return redirect('/terms')

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('log.html', alert='')

@app.route('/register', methods=['GET'])
def register_get():
    return render_template('reg.html', alert='')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('token', None)
    return redirect('/login')
@app.route('/terms', methods=['GET'])
@requires_user
def terms(user, alert):
    if alert:
        return render_template('log.html', alert=alert)
    return render_template('terms.html', user=user, alert='', terms= Term.query.all(), edit_term= "")
@app.route('/terms/<int:term_id>/edit', methods=['post'])
@requires_user
def terms_edit(user, alert, term_id):
    if alert:
        return render_template('log.html', alert=alert)
    term_name = request.form.get('term_name')
    term_description = request.form.get('term_description')
    if not term_name or not term_description:
        return render_template('terms.html', user=user, alert='Missing data', terms= Term.query.all(), edit_term= term_id)
    term = Term.query.filter_by(id=term_id).first()
    if not term:
        return render_template('terms.html', user=user, alert='Term not found', terms= Term.query.all(), edit_term= "")
    if term.user_id != user.id:
        return render_template('terms.html', user=user, alert='No access', terms=Term.query.all(), edit_term="")
    term.name = term_name
    term.description = term_description
    db.session.commit()
    return redirect('/terms')
@app.route('/terms/<int:term_id>/delete', methods=['GET'])
@requires_user
def terms_delete(user, alert, term_id):
    if alert:
        return render_template('log.html', alert=alert)
    term = Term.query.filter_by(id=term_id).first()
    if not term:
        return render_template('terms.html', user=user, alert='Term not found', terms=Term.query.all(), edit_term="")
    if not term.user_id == user.id:
        return render_template('terms.html', user=user, alert='No access', terms=Term.query.all(), edit_term="")
    db.session.delete(term)
    db.session.commit()
    return redirect('/terms')
@app.route('/terms/<int:term_id>/edit', methods=['GET'])
@requires_user
def terms_edit_get(user, alert, term_id):
    if alert:
        return render_template('log.html', alert=alert)
    term = Term.query.filter_by(id=term_id).first()
    if not term:
        return render_template('terms.html', user=user, alert='Term not found', terms=Term.query.all(), edit_term="")
    if term.user_id != user.id:
        return render_template('terms.html', user=user, alert='No access', terms=Term.query.all(), edit_term="")
    return render_template('terms.html', user=user, alert='', terms= Term.query.all(), edit_term= term_id)

@app.route('/terms/add', methods=['POST'])
@requires_user
def terms_add(user, alert):
    if alert:
        return render_template('log.html', alert=alert)
    term_name = request.form.get('term_name')
    term_description = request.form.get('term_description')
    if not term_name or not term_description:
        return render_template('terms.html', user=user, alert='Missing data', terms=Term.query.all(), edit_term="")
    term = Term(name=term_name, description=term_description, user_id=user.id, user_name=user.login)
    db.session.add(term)
    db.session.commit()
    return redirect('/terms')
@app.route('/interpreteter', methods=['get'])
def interpreteter():
    return render_template('interpreteter.html', alert='')
@app.route('/interpreteter', methods=['post'])
def interpreteter_post():
    text = request.form.get('text')
    if not text:
        return 'eror'
    translate = ''
    for word in text.split(' '):
        tr = Term.query.filter_by(name=word).first()
        if tr:
            translate = tr.description+''
        else:
            translate = word+''
    return render_template('interpreteter.html', translate=translate)
if __name__ == '__main__':
    # запускаем сервер
    app.run(debug=True)