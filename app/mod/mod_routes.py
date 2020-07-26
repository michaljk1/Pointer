# -*- coding: utf-8 -*-
from flask import url_for, flash, render_template, redirect, request
from flask_login import current_user, login_required

from app import db
from app.mod import bp
from app.mod.mod_forms import LoginInfoForm, RoleStudentForm, RoleAdminForm
from app.models.usercourse import User, Student, UserCourse, Admin
from app.services.FileUtil import create_directory
from app.services.QueryUtil import login_query
from app.services.ValidationUtil import validate_role


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, User.Roles['MODERATOR'])
    return redirect(url_for('mod.admin_roles'))


@bp.route('/admin_roles', methods=['GET', 'POST'])
@login_required
def admin_roles():
    validate_role(current_user, User.Roles['MODERATOR'])
    admin_form = RoleAdminForm()
    for student in Student.query.all():
        admin_form.email.choices.append((student.email, student.email))
    if request.method == 'POST' and admin_form.validate_on_submit():
        user = UserCourse.query.filter_by(email=admin_form.email.data).first()
        user.role = User.Roles['ADMIN']
        directory = user.get_directory()
        if directory is not None:
            create_directory(directory)
        db.session.commit()
        flash('Nadano prawa administratora', 'message')
        return redirect(url_for('mod.admin_roles'))
    return render_template('mod/admin_roles.html', admin_form=admin_form)


@bp.route('/student_roles', methods=['GET', 'POST'])
@login_required
def student_roles():
    validate_role(current_user, User.Roles['MODERATOR'])
    student_form = RoleStudentForm()
    for admin in Admin.query.all():
        student_form.email.choices.append((admin.email, admin.email))
    if request.method == 'POST' and student_form.validate_on_submit():
        user = UserCourse.query.filter_by(email=student_form.email.data).first()
        user.role = User.Roles['STUDENT']
        db.session.commit()
        flash('Nadano prawa studenta', 'message')
        return redirect(url_for('mod.student_roles'))
    return render_template('mod/student_roles.html', student_form=student_form)


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, User.Roles['MODERATOR'])
    form = LoginInfoForm()
    for user in User.query.all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        logins = login_query(form, current_user.role).all()
        return render_template('adminmod/logins.html', form=form, logins=logins)
    return render_template('adminmod/logins.html', form=form, logins=[])
