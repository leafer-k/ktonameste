import code
from string import ascii_letters
import random
from numpy import number
import pandas as pd
from flask import Blueprint, flash, redirect, render_template, request, url_for
import os

from website import views
from .models import Attendance, Schools, User, Student, Schools
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user, user_accessed
from .message_handler import send_message
from .scripts.generate_code import generate_codes

auth = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'temp'

def generate_code(length):
    code = ""
    for i in range(0, length):
        code += random.choice(ascii_letters)
    return code



@auth.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'POST':
        emailPhone = request.form.get('emailPhone')
        password = request.form.get('password')

        user = User.query.filter_by(email = emailPhone).first()
        if not user:
            user = User.query.filter_by(phone = emailPhone.replace('-', '').replace(' ', '')[-10:]).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('Вы успешно вошли  в аккаунт!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Неверный пароль!', category='error')
        else:
            flash('Такой пользователь не зарегистрирован!', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/statistics')
@login_required
def statistics():   

    return render_template("statistics.html", user=current_user)

@auth.route('/sign-up', methods=['get', 'post'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone').replace('-', '').replace(' ', '')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()
        if not user:
            user = User.query.filter_by(phone = phone).first()

        if user:
            flash('Пользователь с таким email или телефоном уже зарегистрирован!', category='error')
        elif len(email) < 4:
            flash('Адрес почты слишком короткий. Придумайте подлиннее.', category='error')
            pass
        elif len(name) < 2:
            flash('Имя должно иметь хотя бы 2 буквы. Надеемся, никто не обиделся.', category='error')
            pass
        elif len(phone) > 12 or len(phone) < 11 or (phone[0] != '+' and phone[0] != '8'):
            flash('Номер телефона некорректен!', category='error')
            pass
        elif password1 != password2:
            flash('Пароли не совпадают. Проверьте внимательнее!', category='error')
            pass
        elif len(password1) < 7:
            flash('Пароль должен быть длиной как минимум в 7 символов. Вам же лучше.', category='error')
            pass
        else:
            if request.form.get('teachercode'):
                teacher_code = request.form.get('teachercode')
                school = Schools.query.filter_by(school_teachers_code = teacher_code).first()

                if teacher_code == 'EFAnJqSThwQ0KXeqgmrm':
                    new_user = User(email=email, password=generate_password_hash(password1, method='sha256'), name=name, phone=phone[-10:], tgchatid='null', user_type='admin', school_code = 'admin')
                    flash(f'Вы успешно зарегистрированы как админ! Поздравляем.', category='success')
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=True)
                    return redirect(url_for('views.home'))

                elif Schools.query.filter_by(school_moderator_code = teacher_code).first():
                    school = Schools.query.filter_by(school_moderator_code = teacher_code).first()
                    new_user = User(email=email, password=generate_password_hash(password1, method='sha256'), name=name, phone=phone[-10:], tgchatid='null', user_type='moderator', school_code=school.school_code)
                    flash(f'Вы успешно зарегистрированы как модератор! Поздравляем.', category='success')
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=True)
                    return redirect(url_for('views.home'))
                    
                school = Schools.query.filter_by(school_teachers_code = request.form.get('teachercode')).first()
                if school:
                    new_user = User(email=email, password=generate_password_hash(password1, method='sha256'), name=name, phone=phone[-10:], tgchatid='null', user_type='teacher', school_code=school.school_code)
                    flash(f'Вы успешно зарегистрированы как учитель школы {school.school_name}! Поздравляем.', category='success')
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user, remember=True)
                else:
                    flash('Неверный код учителя!', category='error')
            else:
                new_user = User(email=email, password=generate_password_hash(password1, method='sha256'), name=name, phone=phone[-10:], tgchatid='null', user_type='user', school_code=-1)
                db.session.add(new_user)
                db.session.commit()
                flash('Вы успешно зарегистрированы! Поздравляем.', category='success')
                login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/profile', methods=['get', 'post'])
@login_required
def profile():
    if request.method == 'POST':

        if request.form.get('role') == 'connect':

            studentCode = request.form.get('studentCode')
            schoolCode = request.form.get('schoolCode')
            student = Student.query.filter_by(code=studentCode, school_code=schoolCode).first()

            if not student:
                flash('Неверный код.', category='error')
                pass
            else:
                if student.parent_id == -1:
                    student.parent_id = current_user.id
                    db.session.commit()
                    flash(student.name + ' успешно привязан(-а) в вашему аккаунту!', category='success')
                else:
                    flash('Данный ученик уже привязан к другому аккаунту.', category='error')
                    
        elif request.form.get('role') == 'tgConnect':
            current_user.tgchatid = 'tg' + generate_code(8)
            db.session.commit()
        elif request.form.get('role') == 'tgClear':
            send_message(chat_id = current_user.tgchatid, text='Вы отвязали аккаунт.')
            current_user.tgchatid = 'null'
            db.session.commit()

    return render_template("profile.html", user=current_user)
    