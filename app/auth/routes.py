from flask import render_template, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from werkzeug.utils import redirect
from werkzeug.urls import url_parse

from app.DefaultUtil import get_current_date
from app.models.logininfo import LoginInfo
from app.models.usercourse import User, Course, role
from app import db
from app.services.RouteService import validate_exists, redirect_for_index_by_role


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.view_courses'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_info = LoginInfo(ip_address=request.remote_addr, status=LoginInfo.Status['SUCCESS'], user_id=user.id,
                               login_date=get_current_date())
        db.session.add(login_info)
        if not user.check_password(form.password.data):
            login_info.status = LoginInfo.Status['ERROR']
            db.session.commit()
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if current_user.role == role['ADMIN']:
                next_page = url_for('admin.view_courses')
            elif current_user.role == role['STUDENT']:
                next_page = url_for('student.view_courses')
            elif current_user.role == role['MODERATOR']:
                next_page = url_for('mod.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(email=form.email.data, login=form.login.data, name=form.name.data, surname=form.surname.data)
        user.set_password(form.password.data)
        user_amount = len(User.query.all())
        # if user.name == 'Szymon' and \
        #         user.surname == 'Stefański':
        #     user.is_trzodziuch = True
        if user_amount == 0:
            user.role = role['MODERATOR']
        else:
            user.role = role['STUDENT']
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        login_info = LoginInfo(ip_address=request.remote_addr, status=LoginInfo.Status['SUCCESS'], user_id=user.id,
                               login_date=get_current_date())
        db.session.add(login_info)
        db.session.commit()
        return redirect_for_index_by_role(user.role)
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('link/<string:link>')
@login_required
def append_course(link):
    course_by_link = Course.query.filter_by(link=link).first()
    validate_exists(course_by_link)
    if not course_by_link.is_open:
        flash('Przypisanie do kursu nie jest obecnie możliwe')
        return redirect_for_index_by_role(current_user.role)
    elif course_by_link not in current_user.courses:
        current_user.courses.append(course_by_link)
        db.session.commit()
        flash('Przypisano do kursu')
    else:
        flash('Użytkownik przypisany do kursu')
    if current_user.role == role['ADMIN']:
        return redirect(url_for('admin.view_course', course_name=course_by_link.name))
    elif current_user.role == role['STUDENT']:
        return redirect(url_for('student.view_course', course_name=course_by_link.name))
    elif current_user.role == role['MODERATOR']:
        return redirect(url_for('mod.index'))
