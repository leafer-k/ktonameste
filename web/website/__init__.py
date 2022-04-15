from datetime import date
from email import message
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import check_password_hash

from .message_handler import *


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uNP8fuZBjgLZa7QJgcCMpe'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = 'website/upload'
    app.config['MAX_CONTENT_PATH'] = 20971520
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}
    
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin_panel import admin_panel
    from .teacher_panel import teacher_panel

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin_panel)
    app.register_blueprint(teacher_panel)

    from .models import User, Student, Attendance

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.route('/',methods=["GET", "POST"])
    def receive_update():
        if request.method == "POST":
            print(request.json)
            if on_recieve(request.json) == 'connect':
                chatId = request.json["message"]["chat"]["id"]
                text = request.json["message"]["text"]
                if len(text.split()) == 2:
                    if text.split()[1]:
                        user = User.query.filter_by(tgchatid = text.split()[1]).first()
                        if user:
                            if user.tgchatid[0] == 't' and user.tgchatid[1] == 'g':
                                user.tgchatid = chatId
                                db.session.commit()
                                send_message(chat_id=chatId, text='Ваш аккаунт успешно привязан!')
                        elif User.query.filter_by(tgchatid = chatId).first():
                            send_message(chat_id=chatId, text='Этот аккаунт уже привязан!')
                        else:
                            send_message(chat_id=chatId, text='Неверный код!')

        return {"ok": True}

    @app.route('/attendanceRequest', methods=["GET", "POST"])
    def recieve_package():
        if request.method == "POST":
            print(request.json)
            school_code_r = str(int(request.json["code"])[:6]).zfill(6)
            student_code = str(int(request.json["code"]).replace(school_code_r, '')).zfill(6)
            date = request.json["date"]
            time = request.json["time"]
            student = Student.query.filter_by(code = student_code, school_code = school_code_r).first()
            if student:
                new_attendance = Attendance(student_id = student.id,
                date = date, time = time)
                db.session.add(new_attendance)
                db.session.commit()
                parent = User.query.filter_by(id = student.parent_id).first()
                if parent and parent.tgchatid != 'null' and parent.tgchatid[0] != 't':
                    send_message(chat_id=parent.tgchatid, text=f'{student.name} пришёл в школу. {time}')
                print('Success!')
            else:
                return {"ok": False}
        return {"ok": True}

    @app.route('/scanner_login', methods=["GET", "POST"])
    def recieve_login():
        if request.method == "POST":
            data = request.json
            login = data["login"]
            password = data["password"]

            user = User.query.filter_by(email = login).first()
        if not user:
            user = User.query.filter_by(phone = login.replace('-', '').replace(' ', '')[-10:]).first()
        
        if user:
            if check_password_hash(user.password, password):
                if user.user_type == 'teacher' or user.user_type == 'moderator':
                    status_code = 202
                else:
                    status_code = 406
            else:
                status_code = 406
        else:
            status_code = 406

        data = {'name': 'nabin khadka'}
        response = app.response_class(
                    response=json.dumps({"ok":"True"}),
                    status=status_code,
                    mimetype='application/json'
                )

        return jsonify(data), status_code
    return app




def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created database')


create_app().run(debug=True)