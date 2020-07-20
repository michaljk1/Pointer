#!/usr/bin/env python
import os
from flask import url_for, flash, render_template, redirect, request
from flask_login import current_user, login_required
from sqlalchemy import desc
from app import db
from app.mod.mod_forms import LoginInfoForm, RoleStudentForm, RoleAdminForm, DomainForm
from app.mod import bp
from app.models.domain import Domain
from app.models.usercourse import User
from app.services.QueryUtil import login_query
from app.services.ValidationUtil import validate_role


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, User.Roles['MODERATOR'])
    return redirect(url_for('mod.add_domain'))


@bp.route('/add_domain', methods=['GET', 'POST'])
@login_required
def add_domain():
    validate_role(current_user, User.Roles['MODERATOR'])
    form = DomainForm()
    domains = Domain.query.all()
    if request.method == 'POST' and form.validate_on_submit():
        domain = Domain(name=form.domain.data)
        db.session.add(domain)
        db.session.commit()
        return redirect(url_for('mod.add_domain'))
    return render_template('mod/domains.html', form=form, domains=domains)


@bp.route('/admin_roles', methods=['GET', 'POST'])
@login_required
def admin_roles():
    validate_role(current_user, User.Roles['MODERATOR'])
    admin_form = RoleAdminForm()
    for user in User.query.filter(User.role == User.Roles['STUDENT']).all():
        admin_form.email.choices.append((user.email, user.email))
    if request.method == 'POST' and admin_form.validate_on_submit():
        user = User.query.filter_by(email=admin_form.email.data).first()
        user.role = User.Roles['ADMIN']
        directory = user.get_directory()
        if directory is not None and not os.path.exists(directory):
            os.makedirs(directory)
        db.session.commit()
        flash('Nadano prawa administratora', 'message')
        return redirect(url_for('mod.admin_roles'))
    return render_template('mod/admin_roles.html', admin_form=admin_form)


@bp.route('/student_roles', methods=['GET', 'POST'])
@login_required
def student_roles():
    validate_role(current_user, User.Roles['MODERATOR'])
    student_form = RoleStudentForm()
    for user in User.query.filter(User.role == User.Roles['ADMIN']).all():
        student_form.email.choices.append((user.email, user.email))
    if request.method == 'POST' and student_form.validate_on_submit():
        user = User.query.filter_by(email=student_form.email.data).first()
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
    for user in User.query.filter(User.role == User.Roles['ADMIN']).all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        logins = login_query(form, current_user.role).order_by(desc(User.email)).all()
        return render_template('adminmod/logins.html', form=form, logins=logins)
    return render_template('adminmod/logins.html', form=form, logins=[])
