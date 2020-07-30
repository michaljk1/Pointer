# -*- coding: utf-8 -*-
from flask import url_for, flash, render_template, redirect, request
from flask_login import current_user, login_required

from app import db
from app.admin import bp
from app.admin.admin_forms import LoginInfoForm, RoleStudentForm, RoleTeacherForm
from app.models.usercourse import User, Student, UserCourse, Teacher
from app.services.FileUtil import create_directory
from app.services.QueryUtil import login_query
from app.services.ValidationUtil import validate_role


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, User.Roles['ADMIN'])
    return redirect(url_for('admin.teacher_roles'))


@bp.route('/teacher_roles', methods=['GET', 'POST'])
@login_required
def teacher_roles():
    validate_role(current_user, User.Roles['ADMIN'])
    teacher_form = RoleTeacherForm()
    for student in Student.query.all():
        teacher_form.email.choices.append((student.email, student.email))
    if request.method == 'POST' and teacher_form.validate_on_submit():
        user = UserCourse.query.filter_by(email=teacher_form.email.data).first()
        user.role = User.Roles['TEACHER']
        directory = user.get_directory()
        if directory is not None:
            create_directory(directory)
        db.session.commit()
        flash('Nadano prawa teacheristratora', 'message')
        return redirect(url_for('admin.teacher_roles'))
    return render_template('admin/teacher_roles.html', teacher_form=teacher_form)


@bp.route('/student_roles', methods=['GET', 'POST'])
@login_required
def student_roles():
    validate_role(current_user, User.Roles['ADMIN'])
    student_form = RoleStudentForm()
    for teacher in Teacher.query.all():
        student_form.email.choices.append((teacher.email, teacher.email))
    if request.method == 'POST' and student_form.validate_on_submit():
        user = UserCourse.query.filter_by(email=student_form.email.data).first()
        user.role = User.Roles['STUDENT']
        db.session.commit()
        flash('Nadano prawa studenta', 'message')
        return redirect(url_for('admin.student_roles'))
    return render_template('admin/student_roles.html', student_form=student_form)


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, User.Roles['ADMIN'])
    form = LoginInfoForm()
    for user in User.query.all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        logins = login_query(form, current_user.role).all()
        return render_template('teacheradmin/logins.html', form=form, logins=logins)
    return render_template('teacheradmin/logins.html', form=form, logins=[])
