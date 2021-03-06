# -*- coding: utf-8 -*-
from flask import render_template, request, send_from_directory, abort
from flask_login import login_required, current_user

from app.teacher import bp
from app.teacher.TeacherUtil import get_statistics, get_students_emails_from_courses
from app.teacher.teacher_forms import StatisticsForm
from app.admin.admin_forms import LoginInfoForm
from app.models.export import Export
from app.models.lesson import Lesson
from app.models.solution import Solution
from app.models.test import Test
from app.models.usercourse import Course, User, Student
from app.services.QueryUtil import login_query
from app.services.ValidationUtil import validate_course, validate_role


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, User.Roles['TEACHER'])
    form, logins = LoginInfoForm(), []
    emails = get_students_emails_from_courses(current_user.courses)
    emails.append(current_user.email)
    form.email.choices += ((email, email) for email in emails)
    if form.validate_on_submit():
        logins = login_query(form, current_user.role, emails).all()
    return render_template('teacheradmin/logins.html', form=form, logins=logins)


@bp.route('/statistics', methods=['GET', 'POST'])
@login_required
def view_statistics():
    validate_role(current_user, User.Roles['TEACHER'])
    form = StatisticsForm()
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    form.email.choices += ((email, email) for email in get_students_emails_from_courses(current_user.courses))
    statistics_list, statistics_info = [], []
    if request.method == 'POST' and form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        course = Course.query.filter_by(name=form.course.data).first()
        statistics_list, statistics_info = get_statistics(student, course, current_user.courses)
    return render_template('teacher/statistics.html', statisticsList=statistics_list, statistics_info=statistics_info,
                           form=form)


@bp.route('/download')
@login_required
def download():
    validate_role(current_user, User.Roles['TEACHER'])
    request_id = request.args.get('id')
    domain = request.args.get('domain')
    my_object, my_course, filename = None, None, None
    if domain == 'test':
        my_object = Test.query.filter_by(id=request_id).first()
        filename = request.args.get('filename')
        my_course = my_object.get_course()
    elif domain == 'solution':
        my_object = Solution.query.filter_by(id=request_id).first()
        my_type = request.args.get('type')
        if my_type == 'output':
            filename = my_object.output_file
        else:
            filename = my_object.filename
        my_course = my_object.get_course()
    elif domain == 'export':
        my_object = Export.query.filter_by(id=request_id).first()
        filename = my_object.file_name
    elif domain == 'lesson':
        my_object = Lesson.query.filter_by(id=request_id).first()
        filename = my_object.content_pdf_path
        my_course = my_object.get_course()
    else:
        abort(404)
    if domain == 'export':
        if my_object.user_id != current_user.id:
            abort(404)
    else:
        validate_course(current_user, User.Roles['TEACHER'], my_course)
    return send_from_directory(directory=my_object.get_directory(), filename=filename)
