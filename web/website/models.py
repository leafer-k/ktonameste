from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Schools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_code = db.Column(db.Integer, unique=True)
    school_name = db.Column(db.String(150))
    school_teachers_code = db.Column(db.String(150), unique=True)
    school_moderator_code = db.Column(db.String(150), unique=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(150), db.ForeignKey('student.id'))
    date = db.Column(db.String(150))
    time = db.Column(db.String(150))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(150))
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    student_class = db.Column(db.String(150))
    student_grade = db.Column(db.Integer)
    student_attendance = db.relationship('Attendance')
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    school_code = db.Column(db.Integer)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    phone = db.Column(db.String(150), unique=True)
    student_id = db.relationship('Student')
    tgchatid = db.Column(db.String(150))
    user_type = db.Column(db.String(150))
    school_code = db.Column(db.Integer)
