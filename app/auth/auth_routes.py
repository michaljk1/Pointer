#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.auth import bp
from app.auth.auth_forms import LoginForm, RegistrationForm, ConfirmEmailForm, ChangePasswordForm, ResetPasswordForm
from werkzeug.utils import redirect
from werkzeug.urls import url_parse
from app.services.DateUtil import get_current_date
from app.models.logininfo import LoginInfo
from app.models.usercourse import User, Course
from app import db
from app.services.ValidationUtil import validate_exists


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.view_courses'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User.query.filter_by(login=form.email.data).first()
        if user is None:
            flash('Nieprawidłowe dane', 'message')
            return redirect(url_for('auth.login'))
        login_info = LoginInfo(ip_address=request.remote_addr, status=LoginInfo.Status['SUCCESS'], user_id=user.id,
                               login_date=get_current_date())
        db.session.add(login_info)
        if not user.check_password(form.password.data):
            login_info.status = LoginInfo.Status['ERROR']
            db.session.commit()
            flash('Niepoprawne dane', 'error')
            return redirect(url_for('auth.login'))
        if not user.is_confirmed:
            login_info.status = LoginInfo.Status['ERROR']
            db.session.commit()
            flash('Aktywuj swoje konto')
            return redirect(url_for('auth.activate'))
        login_user(user, remember=form.remember_me.data)
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('default.index'))
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/activate', methods=['GET', 'POST'])
def activate():
    form = ConfirmEmailForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.launch_email('send_confirm_email', 'confirm email')
        flash('Wysłano link aktywacyjny', 'message')
        return redirect(url_for('auth.login'))
    return render_template('auth/activate.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(email=form.email.data, login=form.login.data, name=form.name.data, surname=form.surname.data,
                    role=User.Roles['STUDENT'], index=form.index.data)
        user.set_password(form.password.data)
        db.session.add(user)
        user.launch_email('send_confirm_email', 'confirm email')
        db.session.commit()
        flash('Rejestracja zakończona, potwierdź adres email', 'message')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        if current_user.check_password(form.actual_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Zmieniono hasło', 'message')
            return redirect(url_for('default.index'))
        else:
            flash('Błędne hasło', 'error')
    return render_template('auth/change_password.html', form=form)


@bp.route('reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    user: User = User.verify_reset_password_token(token)
    if not user:
        flash('Nieaktywny link', 'error')
        return redirect(url_for('default.index'))
    if request.method == 'POST' and form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Zmieniono hasło', 'message')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('send_reset', methods=['GET', 'POST'])
def send_reset():
    form = ConfirmEmailForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.launch_email('send_reset_password', 'reset password')
        flash('Wysłano wiadomość', 'message')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('link/<string:link>')
@login_required
def append_course(link):
    course_by_link = Course.query.filter_by(link=link).first()
    validate_exists(course_by_link)
    if not course_by_link.is_open:
        flash('Przypisanie do kursu nie jest obecnie możliwe')
        return redirect(url_for('default.index'))
    elif course_by_link not in current_user.courses:
        current_user.courses.append(course_by_link)
        db.session.commit()
        flash('Przypisano do kursu')
    else:
        flash('Użytkownik przypisany do kursu')
    return redirect(url_for('default.index'))


@bp.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    user: User = User.verify_confirm_email_token(token)
    if not user:
        flash('Nieaktywny link', 'error')
        return redirect(url_for('default.index'))
    user.is_confirmed = True
    db.session.commit()
    flash('Potwierdzono email', 'message')
    if not current_user.is_authenticated:
        flash('Potwierdzono email, zaloguj się')
        return redirect(url_for('auth.login'))
    return redirect(url_for('default.index'))
