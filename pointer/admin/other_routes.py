# TODO
# maksymalna ilosc pamieci, student statystyki
from flask import render_template, request, send_from_directory, abort
from flask_login import login_required, current_user
from sqlalchemy import desc
from pointer.admin import bp
from pointer.admin.AdminUtil import get_students_ids_emails, get_statistics
from pointer.admin.admin_forms import StatisticsForm
from pointer.mod.mod_forms import LoginInfoForm
from pointer.models.test import Test
from pointer.models.usercourse import Course, User, role
from pointer.models.export import Export
from pointer.models.lesson import Lesson
from pointer.models.solution import Solution
from pointer.services.QueryService import login_query
from pointer.services.RouteService import validate_role_course, validate_role


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, role['ADMIN'])
    form, logins = LoginInfoForm(), []
    user_ids, emails = get_students_ids_emails(current_user.courses)
    form.email.choices += ((email, email) for email in emails)
    if form.validate_on_submit():
        logins = login_query(form, current_user.role, ids=user_ids).order_by(desc(User.email)).all()
    return render_template('adminmod/logins.html', form=form, logins=logins)


@bp.route('/statistics', methods=['GET', 'POST'])
@login_required
def view_statistics():
    validate_role(current_user, role['ADMIN'])
    form = StatisticsForm()
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    form.email.choices += ((email, email) for email in get_students_ids_emails(current_user.courses)[1])
    statistics_list, statistics_info = [], []
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        course = Course.query.filter_by(name=form.course.data).first()
        statistics_list, statistics_info = get_statistics(user, course, current_user.courses)
    return render_template('admin/statistics.html', statisticsList=statistics_list, statistics_info=statistics_info,
                           form=form)


@bp.route('/download')
@login_required
def download():
    validate_role(current_user, role['ADMIN'])
    request_id = request.args.get('id')
    domain = request.args.get('domain')
    my_object, my_course, filename = None, None, None
    if domain == 'test':
        my_object = Test.query.filter_by(id=request_id).first()
        filename = request.args.get('filename')
        my_course = my_object.get_course()
    elif domain == 'solution':
        my_object = Solution.query.filter_by(id=request_id).first()
        filename = my_object.file_path
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
    if domain != 'export':
        validate_role_course(current_user, role['ADMIN'], my_course)
    return send_from_directory(directory=my_object.get_directory(), filename=filename)
