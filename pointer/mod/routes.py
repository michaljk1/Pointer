import os

from flask import url_for, flash, render_template, redirect, request
from flask_login import current_user, login_required
from sqlalchemy import desc

from pointer import db
from pointer.mod.forms import LoginInfoForm, RoleStudentForm, RoleAdminForm
from pointer.mod import bp
from pointer.models.usercourse import role, User
from pointer.services.QueryService import login_query
from pointer.services.RouteService import validate_role


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, role['MODERATOR'])
    return redirect(url_for('mod.admin_roles'))


@bp.route('/admin_roles', methods=['GET', 'POST'])
@login_required
def admin_roles():
    validate_role(current_user, role['MODERATOR'])
    admin_form = RoleAdminForm()
    for user in User.query.filter(User.role == role['STUDENT']).all():
        admin_form.email.choices.append((user.email, user.email))
    if request.method == 'POST' and admin_form.validate_on_submit():
        user = User.query.filter_by(email=admin_form.email.data).first()
        user.role = role['ADMIN']
        directory = user.get_admin_directory()
        if not os.path.exists(directory):
            os.makedirs(directory)
        db.session.commit()
        flash('Nadano prawa administratora')
        return redirect(url_for('mod.admin_roles'))
    return render_template('mod/admin_roles.html', admin_form=admin_form)


@bp.route('/student_roles', methods=['GET', 'POST'])
@login_required
def student_roles():
    validate_role(current_user, role['MODERATOR'])
    student_form = RoleStudentForm()
    for user in User.query.filter(User.role == role['ADMIN']).all():
        student_form.email.choices.append((user.email, user.email))
    if request.method == 'POST' and student_form.validate_on_submit():
        user = User.query.filter_by(email=student_form.email.data).first()
        user.role = role['STUDENT']
        db.session.commit()
        flash('Nadano prawa studenta')
        return redirect(url_for('mod.student_roles'))
    return render_template('mod/student_roles.html', student_form=student_form)


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, role['MODERATOR'])
    form = LoginInfoForm()
    for user in User.query.filter(User.role == role['ADMIN']).all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        logins = login_query(form, current_user.role).order_by(desc(User.email)).all()
        return render_template('mod/logins.html', form=form, logins=logins)
    return render_template('mod/logins.html', form=form, logins=[])
