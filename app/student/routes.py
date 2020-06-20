import os
import shutil
from datetime import datetime, timedelta

import pytz
from flask import render_template, url_for, request, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import desc

from app.services.ExerciseService import compile, grade
from app.services.QueryService import exercise_query
from app.services.RouteService import validate_role, validate_role_course, validate_role_solution
from app.student import bp
from app.student.forms import UploadForm, SolutionStudentSearchForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, Exercise, Lesson, Solution, role
from app import db


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, role['STUDENT'])
    return redirect(url_for('student.view_courses'))


@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    validate_role(current_user, role['STUDENT'])
    return render_template('student/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['STUDENT'], course)
    return render_template('student/course.html', course=course)


@bp.route('<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    validate_role(current_user, role['STUDENT'])
    return render_template('student/lesson.html', lesson=Lesson.query.filter_by(id=lesson_id).first())


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['STUDENT'], exercise.get_course())
    form = UploadForm()
    attempts = len(exercise.get_user_solutions(current_user.id))
    current_datetime = datetime.now(pytz.timezone('Europe/Warsaw'))
    end_date = exercise.end_date
    end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_date.hour,
                            minute=end_date.minute, tzinfo=current_datetime.tzinfo)
    solution = Solution.query.filter_by(exercise_id=exercise.id, user_id=current_user.id).order_by(
        desc(Solution.send_date)).first()
    show_score = current_datetime < end_datetime
    if solution is None:
        proper_date = show_score
    else:
        send_date = solution.send_date.replace(tzinfo=current_datetime.tzinfo)
        proper_date = (current_datetime < end_datetime) and (current_datetime - send_date) > timedelta(
            seconds=exercise.timeout)
    if form.validate_on_submit():
        file = request.files['file']
        filename = secure_filename(file.filename)
        solution = Solution(user_id=current_user.id, exercise_id=exercise.id, file_path=filename, points=0,
                            ip_address=request.remote_addr, os_info=str(request.user_agent), attempt=attempts,
                            status=Solution.solutionStatus['SEND'],
                            send_date=datetime.now(pytz.timezone('Europe/Warsaw')))
        exercise.solutions.append(solution)
        current_user.solutions.append(solution)
        solution_directory = solution.get_directory()
        os.makedirs(solution_directory)
        file.save(os.path.join(solution_directory, filename))
        if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
                '.tar'):
            shutil.unpack_archive(os.path.join(solution_directory, filename), solution_directory)
        db.session.commit()
        try:
            compile(solution)
            grade(solution)
        except:
            solution.points = 0
            solution.status = Solution.solutionStatus['ERROR']
            solution.is_active = False
            db.session.commit()
        return redirect(url_for('student.view_exercise', exercise_id=exercise.id))
    return render_template('student/exercise.html', exercise=exercise, form=form, proper_date=proper_date,
                           show_score=show_score,
                           solutions=exercise.get_user_solutions(current_user.id))


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, role['STUDENT'])
    form = SolutionStudentSearchForm()
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        solutions = exercise_query(form=form, courses=current_user.get_course_names(), user_id=current_user.id).all()
        return render_template('student/solutions.html', form=form, solutions=solutions,
                               datetime=datetime.now(pytz.timezone('Europe/Warsaw')))
    return render_template('student/solutions.html', form=form, solutions=[],
                           datetime=datetime.now(pytz.timezone('Europe/Warsaw')))


@bp.route('/uploads/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
def download_content(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_role_course(current_user, role['STUDENT'], lesson.course)
    return send_from_directory(directory=lesson.get_directory(), filename=lesson.content_pdf_path)


@bp.route('/mysolution/<int:solution_id>/', methods=['GET', 'POST'])
@login_required
def download_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_role_solution(current_user, role['STUDENT'], solution)
    return send_from_directory(directory=solution.get_directory(), filename=solution.file_path)
