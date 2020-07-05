import os
import string
import random
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from pointer.admin import bp
from pointer.auth.email import send_course_email
from pointer.admin.forms import CourseForm, SelectStudentForm, ViewStudentStatsForm
from werkzeug.utils import redirect
from pointer.models.usercourse import Course, User, role
from pointer import db
from pointer.services.RouteService import validate_role_course, validate_role


@bp.route('/')
@bp.route('/index')
@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    validate_role(current_user, role['ADMIN'])
    return render_template('admin/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>', methods=['GET', 'POST'])
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = ViewStudentStatsForm()
    for student in course.get_students():
        form.email.choices.append((student.email, student.email))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
    return render_template('admin/course.html', course=course, form=form)


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
@login_required
def add_student(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = SelectStudentForm()
    for user in User.query.filter(~User.courses.any(name=course.name)).filter(
            User.role.in_([role['ADMIN'], role['STUDENT']])).all():
        # TODO do zmiany         User.role.in_([role['ADMIN'], role['STUDENT']])).filter(User.is_confirmed).all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
        send_course_email(form.email.data, course_name=course.name, role=user.role)
        db.session.commit()
        flash('Dodano studenta', 'message')
        return redirect(url_for('admin.add_student', course_name=course.name))
    return render_template('admin/add_student.html', form=form, course=course)


@bp.route('/change_open/<int:course_id>', methods=['GET', 'POST'])
@login_required
def change_open_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    validate_role_course(current_user, role['ADMIN'], course)
    course.is_open = not course.is_open
    db.session.commit()
    flash('Zapisano zmiany', 'message')
    return redirect(url_for('admin.view_course', course_name=course.name))


@bp.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    validate_role(current_user, role['ADMIN'])
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_course = Course(name=form.name.data, is_open=True,
                            link=''.join(random.choice(string.ascii_lowercase) for i in range(25)))
        current_user.courses.append(new_course)
        os.makedirs(new_course.get_directory())
        db.session.commit()
        flash('Dodano kurs', 'message')
        return redirect(url_for('admin.view_courses'))
    return render_template('admin/add_course.html', form=form)
