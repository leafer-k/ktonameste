from website import views
from .models import Schools, User, Student, Schools
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user, user_accessed
from . import db

admin_panel = Blueprint('admin_panel', __name__)

@admin_panel.route('/admin_panel', methods=['get', 'post'])
@login_required
def panel():
    schools = Schools.query.all()
    print(schools)
    if current_user.user_type != 'admin':
        flash('Доступ запрещён!', category='error')
        return redirect(url_for('views.home'))
    else:
        if request.method == 'POST':
            if request.form.get('role') == 'newSchool':
                schoolCode = request.form.get('schoolCode')
                schoolName = request.form.get('schoolName')
                teacherCode = request.form.get('teacherCode')
                moderatorCode = request.form.get('moderatorCode')

                if Schools.query.filter_by(school_code = schoolCode).first():
                    flash('Такая школа уже загеристрирована!', category='error')
                else:
                    new_school = Schools(school_code = schoolCode, school_name = schoolName, school_teachers_code = teacherCode, school_moderator_code = moderatorCode)
                    db.session.add(new_school)
                    db.session.commit()
                    flash(f'{schoolName} добавлена!', category='success')
            redirect(url_for('admin_panel.panel'))
        return render_template("admin_panel.html", user=current_user, schools=schools)