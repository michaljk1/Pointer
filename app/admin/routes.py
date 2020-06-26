import os
import string
import random
# TODO
# 1: obsluga maili, wyniki pdf,
# 2: modyfikacja istniejacych obiektow, timeout testu, statystyki dla kursu i uzytkownika
# 4: paginacja + order by przy wynikach, zalezne formularze w js
# 5: selenium, backup, mysql -> sqlite, osmkdirs
from datetime import datetime

from flask import render_template, url_for, flash, request, send_from_directory, current_app, abort
from flask_login import logout_user, login_required, current_user
from sqlalchemy import desc
from app.admin import bp
from app.admin.AdminUtil import modify_solution, get_student_ids_emails
from app.auth.email import send_confirm_email, send_course_email
from app.admin.forms import CourseForm, ExerciseForm, LessonForm, AssigneUserForm, SolutionForm, \
    SolutionAdminSearchForm, EnableAssingmentLink, TestForm, StatisticsCourseForm, StatisticsUserForm
from werkzeug.utils import redirect, secure_filename
from app.DefaultUtil import get_current_date
from app.mod.forms import LoginInfoForm
from app.models.statistics import Statistics
from app.models.test import Test
from app.models.usercourse import Course, User, role
from app.models.solutionexport import SolutionExport
from app.models.lesson import Lesson
from app.models.exercise import Exercise

from app import db
from app.models.solution import Solution
from app.services.ExerciseService import accept_best_solution
from app.services.ExportService import create_csv_export
from app.services.QueryService import exercise_query, login_query
from app.services.RouteService import validate_exists, validate_role_course, validate_role


@bp.route('/logout')
@login_required
def logout():
    validate_role(current_user, role['ADMIN'])
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
@login_required
def add_student(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = AssigneUserForm()
    for user in User.query.filter(~User.courses.any(name=course.name)).filter(
            User.role.in_([role['ADMIN'], role['STUDENT']])).filter(User.is_confirmed).all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
        send_course_email(form.email.data, course_name=course.name, role = user.role)
        db.session.commit()
        flash('Dodano studenta')
    return render_template('admin/add_student.html', form=form, course=course)


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
    form = EnableAssingmentLink(activate=course.is_open)
    if request.method == 'POST' and form.validate_on_submit():
        if form.activate.data:
            course.is_open = True
        else:
            course.is_open = False
        db.session.commit()
        flash('Zapisano zmiany')
        return render_template('admin/course.html', form=form, course=course)
    return render_template('admin/course.html', form=form, course=course)


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
        flash('Dodano kurs')
        return redirect(url_for('admin.view_courses'))
    return render_template('admin/add_course.html', form=form)


@bp.route('/lesson/<string:lesson_name>/')
@login_required
def view_lesson(lesson_name):
    lesson = Lesson.query.filter_by(name=lesson_name).first()
    validate_role_course(current_user, role['ADMIN'], lesson.course)
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
@login_required
def add_lesson(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = LessonForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['pdf_content']
        filename = secure_filename(file.filename)
        if filename == '':
            filename = None
        lesson_name = form.name.data
        new_lesson = Lesson(name=lesson_name, content_pdf_path=filename, content_url=form.content_url.data,
                            raw_text=form.text_content.data)
        course.lessons.append(new_lesson)
        lesson_directory = new_lesson.get_directory()
        os.makedirs(lesson_directory)
        if filename is not None:
            file.save(os.path.join(lesson_directory, filename))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_name=new_lesson.name))
    return render_template('admin/add_lesson.html', form=form, course=course)


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    return render_template('admin/exercise.html', exercise=exercise)


@bp.route('/test/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def add_test(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        db.session.commit()
        flash('Dodano test')
        return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))
    return render_template('admin/add_test.html', exercise=exercise, form=form)


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
@login_required
def add_exercise(course_name, lesson_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_exists(course)
    lesson = course.get_lesson_by_name(lesson_name)
    validate_exists(lesson)
    validate_role_course(current_user, role['ADMIN'], course)
    form = ExerciseForm()
    if form.validate_on_submit():
        end_date, end_time = form.end_date.data, form.end_time.data
        end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour,
                                minute=end_time.minute)
        exercise = Exercise(name=form.name.data, content=form.content.data, lesson_id=lesson.id,
                            max_attempts=form.max_attempts.data, compile_command=form.compile_command.data,
                            end_date=end_datetime, run_command=form.run_command.data,
                            program_name=form.program_name.data, timeout=form.timeout.data)
        lesson.exercises.append(exercise)
        os.makedirs(exercise.get_directory())
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_name=lesson.name))
    return render_template('admin/add_template.html', form=form, lesson=lesson)


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, role['ADMIN'])
    course, lesson, exercise = request.args.get('course'), request.args.get('lesson'), request.args.get('exercise')
    course_db = Course.query.filter_by(name=course).first()
    if course is None or lesson is None or exercise is None or course_db is None or course_db not in current_user.courses:
        form = SolutionAdminSearchForm()
    else:
        form = SolutionAdminSearchForm(course=course, lesson=lesson, exercise=exercise)
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        solutions = exercise_query(form=form, courses=current_user.get_course_names()).all()
        return render_template('admin/solutions.html', form=form, solutions=solutions)
    return render_template('admin/solutions.html', form=form, solutions=[])


@bp.route('/solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def view_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_exists(solution)
    validate_role_course(current_user, role['ADMIN'], solution.get_course())
    solution_form = SolutionForm(obj=solution, email=solution.author.email,
                                 admin_ref=(solution.status == solution.Status['REFUSED']))
    if request.method == 'POST' and solution_form.validate_on_submit():
        modify_solution(solution, solution_form.admin_ref.data, solution_form.points.data)
        accept_best_solution(solution.user_id, solution.exercise)
        flash('Zapisano zmiany')
        return render_template('admin/solution.html', form=solution_form, solution=solution)
    return render_template('admin/solution.html', form=solution_form, solution=solution)


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, role['ADMIN'])
    form = LoginInfoForm()
    user_ids, form.email.choices = get_student_ids_emails(current_user.courses)
    if form.validate_on_submit():
        logins = login_query(form, current_user.role, ids=user_ids).order_by(desc(User.email)).all()
        return render_template('mod/logins.html', form=form, logins=logins)
    return render_template('mod/logins.html', form=form, logins=[])


@bp.route('/export_csv/')
@login_required
def export_csv():
    validate_role(current_user, role['ADMIN'])
    ids = request.args.getlist('ids')
    solutions = Solution.query.filter(Solution.id.in_(ids)).all()
    directory = os.path.join(current_app.instance_path, current_user.login)
    if not os.path.exists(directory):
        os.makedirs(directory)
    export = create_csv_export(solutions, directory, get_current_date(), current_user.id)
    db.session.add(export)
    db.session.commit()
    flash('Wyeksportowano')
    return redirect(url_for('admin.view_exports'))


@bp.route('/view_exports/')
@login_required
def view_exports():
    validate_role(current_user, role['ADMIN'])
    exports = SolutionExport.query.filter_by(user_id=current_user.id).all()
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
    return render_template('admin/statistics_user.html', statisticsList=statistics_list, form=form)


@bp.route('/download')
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
        my_object = SolutionExport.query.filter_by(id=request_id).first()
        filename = my_object.file_name
    else:
        abort(404)
    if my_course is not None:
        validate_role_course(current_user, role['ADMIN'], my_course)
    else:
        validate_role(current_user, role['ADMIN'])
    return send_from_directory(directory=my_object.get_directory(), filename=filename)
