# TODO
# 1: rich editor, wyniki pdf,
# zmiana w eksporcie z zatwierdzonymi zadaniami
# 2: maksymalna ilosc pamieci,
# 4: paginacja, estetyka
from flask import render_template, url_for, flash, request, send_from_directory, abort
from flask_login import logout_user, login_required, current_user
from sqlalchemy import desc
from pointer.admin import bp
from pointer.admin.AdminUtil import get_student_ids_emails
from pointer.admin.forms import StatisticsCourseForm, StatisticsUserForm
from werkzeug.utils import redirect
from pointer.mod.forms import LoginInfoForm
from pointer.models.statistics import Statistics
from pointer.models.test import Test
from pointer.models.usercourse import Course, User, role
from pointer.models.solutionexport import Export
from pointer.models.lesson import Lesson
from pointer.models.solution import Solution
from pointer.services.ExportService import create_csv_solution_export, create_csv_statistics_export
from pointer.services.QueryService import login_query
from pointer.services.RouteService import validate_role_course, validate_role


@bp.route('/logout')
@login_required
def logout():
    validate_role(current_user, role['ADMIN'])
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, role['ADMIN'])
    form, logins = LoginInfoForm(), []
    user_ids, emails = get_student_ids_emails(current_user.courses)
    form.email.choices += emails
    if form.validate_on_submit():
        logins = login_query(form, current_user.role, ids=user_ids).order_by(desc(User.email)).all()
    return render_template('adminmod/logins.html', form=form, logins=logins)


@bp.route('/export_solutions/')
@login_required
def export_solutions():
    validate_role(current_user, role['ADMIN'])
    ids = request.args.getlist('ids')
    solutions = Solution.query.filter(Solution.id.in_(ids)).all()
    create_csv_solution_export(solutions, current_user)
    flash('Wyeksportowano', 'message')
    return redirect(url_for('admin.view_exports'))


@bp.route('/export_statistics/')
@login_required
def export_statistics():
    validate_role(current_user, role['ADMIN'])
    create_csv_statistics_export(request.args.getlist('statistics_json'), current_user)
    flash('Wyeksportowano', 'message')
    return redirect(url_for('admin.view_exports'))


@bp.route('/view_exports/')
@login_required
def view_exports():
    validate_role(current_user, role['ADMIN'])
    exports = Export.query.filter_by(user_id=current_user.id).order_by(desc(Export.generation_date)).all()
    return render_template('admin/exports.html', exports=exports)


@bp.route('/statistics', methods=['GET', 'POST'])
@login_required
def view_statistics():
    validate_role(current_user, role['ADMIN'])
    statistics_list = []
    for course in current_user.courses:
        for member in course.members:
            if member.role == role['STUDENT']:
                statistics_list.append(Statistics(course=course, user=member, is_admin=True))
    return render_template('admin/statistics.html', statisticsList=statistics_list)


@bp.route('/statistics/by_course', methods=['GET', 'POST'])
@login_required
def view_statistics_course():
    validate_role(current_user, role['ADMIN'])
    form = StatisticsCourseForm()
    statistics_list = []
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        course = Course.query.filter_by(name=form.course.data).first()
        for member in course.members:
            if member.role == role['STUDENT']:
                statistics_list.append(Statistics(course=course, user=member, is_admin=True))
    return render_template('admin/statistics_course.html', statisticsList=statistics_list, form=form)


@bp.route('/statistics/by_user', methods=['GET', 'POST'])
@login_required
def view_statistics_user():
    validate_role(current_user, role['ADMIN'])
    form = StatisticsUserForm()
    statistics_list = []
    form.email.choices = get_student_ids_emails(current_user.courses)[1]
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        for course in user.courses:
            if course in current_user.courses:
                statistics_list.append(Statistics(course=course, user=user, is_admin=True))
    return render_template('admin/statistics_user.html', statisticsList=statistics_list, form=form)


@bp.route('/download')
@login_required
def download():
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
    else:
        abort(404)
    if my_course is not None:
        validate_role_course(current_user, role['ADMIN'], my_course)
    else:
        validate_role(current_user, role['ADMIN'])
    return send_from_directory(directory=my_object.get_directory(), filename=filename)
