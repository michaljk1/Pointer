import os
from flask import render_template, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from werkzeug.utils import redirect
from werkzeug.urls import url_parse
from app.models import User, Course, Role
from app import db


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if current_user.role == Role.ADMIN:
                next_page = url_for('admin.view_courses')
            else:
                next_page = url_for('student.view_courses')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, login=form.login.data, name=form.name.data, surname=form.surname.data)
        user.set_password(form.password.data)
        user_amount = len(User.query.all())
        if user_amount == 0:
            user.role = Role.ADMIN
        else:
            user.role = Role.STUDENT
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        if user_amount == 0:
            return redirect(url_for('admin.view_courses'))
        else:
            return redirect(url_for('student.view_courses'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/<string:link>')
@login_required
def append_course(link):
    course_by_link = Course.query.filter_by(link=link).first()
    if course_by_link not in current_user.courses:
        current_user.courses.append(course_by_link)
        db.session.commit()
        flash('Przypisano do kursu')
    else:
        flash('Użytkownik przypisany do kursu')
    if current_user.role == Role.ADMIN:
        return redirect(url_for('admin.view_course', course_name=course_by_link.name))
    else:
        return redirect(url_for('student.view_course', course_name=course_by_link.name))

