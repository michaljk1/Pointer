#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import string
import random
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import bp
from app.admin.admin_forms import CourseForm, DeleteStudentForm, AddStudentForm
from werkzeug.utils import redirect
from app.models.usercourse import Course, User
from app import db
from app.services.ValidationUtil import validate_course, validate_role


@bp.route('/')
@bp.route('/index')
@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    validate_role(current_user, User.Roles['ADMIN'])
    return render_template('admin/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>', methods=['GET', 'POST'])
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['ADMIN'], course)
    return render_template('admin/course.html', course=course)


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
@login_required
def add_student(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['ADMIN'], course)
    form = AddStudentForm()
    for user in User.query.filter(~User.courses.any(name=course.name)).filter(User.role == User.Roles['STUDENT']).all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
        user.launch_course_email(course_name)
        db.session.commit()
        flash('Dodano studenta', 'message')
        return redirect(url_for('admin.add_student', course_name=course.name))
    return render_template('admin/add_student.html', form=form, course=course)


@bp.route('/<string:course_name>/delete_student', methods=['GET', 'POST'])
@login_required
def delete_student(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['ADMIN'], course)
    form = DeleteStudentForm()
    for student in course.get_students():
        form.email.choices.append((student.email, student.email))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.remove(course)
        db.session.commit()
        flash('Usunięto studenta', 'message')
        return redirect(url_for('admin.delete_student', course_name=course.name))
    return render_template('admin/delete_student.html', form=form, course=course)


@bp.route('/change_open/<int:course_id>', methods=['GET', 'POST'])
@login_required
def change_open_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    validate_course(current_user, User.Roles['ADMIN'], course)
    course.is_open = not course.is_open
    db.session.commit()
    flash('Zapisano zmiany', 'message')
    return redirect(url_for('admin.view_course', course_name=course.name))


@bp.route('/add_course', methods=['GET', 'POST'])
@login_required
def add_course():
    validate_role(current_user, User.Roles['ADMIN'])
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
