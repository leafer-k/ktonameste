from website import views
from website.auth import UPLOAD_FOLDER
from .models import Attendance, Schools, User, Student, Schools
from flask import Blueprint, flash, redirect, render_template, request, url_for, send_file
from flask_login import login_required, current_user, user_accessed
from . import db
from .scripts.generate_code import generate_codes
from .scripts.make_codes import makeQrCode
import os
import pandas as pd
import shutil
import glob
from pathlib import Path
from datetime import date

UPLOAD_FOLDER = 'temp'

teacher_panel = Blueprint('teacher_panel', __name__)

@teacher_panel.route('/teacher_panel', methods=['get', 'post'])
@login_required
def teacherPanel():
    if current_user.user_type != 'admin' and current_user.user_type != 'teacher' and current_user.user_type != 'moderator':
        flash('Доступ запрещён!', category='error')
        return redirect(url_for('views.home'))
    else:
        if current_user.user_type == 'admin':
            students = Student.query.all()
            school = 'all'
        else:
            students = Student.query.filter_by(school_code = current_user.school_code)
            school = Schools.query.filter_by(school_code = current_user.school_code).first()

        classes = []
        for std in students:
            if not((str(std.student_grade) + std.student_class) in classes):
                classes.append(str(std.student_grade) + std.student_class)
        classes.sort()
        if request.method == 'POST':
            if "download_codes" in request.form:
                for std in students:
                    qr = makeQrCode(str(std.school_code) + str(std.code))
                    qr.save(os.path.join('website', UPLOAD_FOLDER, 'codes', f'{std.student_grade}{std.student_class}{std.surname}.png'))
                
                archive = shutil.make_archive('qrcodes', 'zip', 'website/temp/codes')

                files = glob.glob('website/temp/codes/*.png')
                for f in files:
                    try:
                        Path(f).unlink()
                    except OSError as e:
                        print("Error: %s : %s" % (f, e.strerror))

                return send_file(Path(archive))
                
            elif request.form.get('role') == 'add':
                studentCode = request.form.get('newStudentCode')
                name =  request.form.get('newStudentName')
                surname = request.form.get('newStudentSurname')
                    
                new_student = Student(code = studentCode, name = name, surname = surname,
                student_grade = (int(studentCode) // 100) % 100, student_class = chr(int(studentCode) % 100),
                parent_id = -1)

                db.session.add(new_student)
                db.session.commit()
                flash('Ученик с кодом ' + studentCode + ' добвлен!', category='success')
            elif request.form.get('role') == 'addAttend':
                time = request.form.get('time')
                curr_date = date.today().strftime("%d.%m.%Y")
                code = request.form.get('studentCode')
                school_code = current_user.school_code

                student = Student.query.filter_by(school_code = school_code, code = code).first()
                if student:
                    print()
                    new_attendance = Attendance(student_id = student.id, date = curr_date, time = time)
                    db.session.add(new_attendance)
                    db.session.commit()
                    flash('Запись добавлена!', category='succsess')
                else:
                    flash('Неверный код!', category='error')
            elif request.form.get('role') == 'excel-import':
                file = request.files['file']
                if file:
                    file.save(os.path.join('website', UPLOAD_FOLDER, 'students-import.xlsx'))
                    data = pd.read_excel(file)
                    fullnames = data['Ф.И.О'].tolist()
                    grades = data['Класс'].tolist()
                    classnames = data['Буква'].tolist()
                    numbers = data['№'].tolist()
                    

                    codes = []
                    
                    for i in range(len(numbers)):
                        codes.append(generate_codes(numbers[i], classnames[i], grades[i]))

                    for i in range(len(codes)):
                        new_student = Student(code=codes[i], name=fullnames[i].split()[1], surname=fullnames[i].split()[0], student_grade=grades[i], student_class=classnames[i], parent_id=-1, school_code=current_user.school_code)
                        if Student.query.filter_by(code=new_student.code, school_code=current_user.school_code).first():
                            print('Ученик уже есть в базе!')
                        else: 
                            db.session.add(new_student)
                    db.session.commit()

                    os.remove(os.path.join('website', UPLOAD_FOLDER, 'students-import.xlsx'))
            else:
                flash('Error!', category='error')
        return render_template("teacher_panel.html", user=current_user, students=students, school=school, classes=classes)