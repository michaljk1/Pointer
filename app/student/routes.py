import os
import shutil
from datetime import datetime

import pytz
from flask import render_template, url_for, request, send_from_directory
from flask_login import login_required, current_user
from app.services.ExerciseService import ExerciseService
from app.services.RouteService import RouteService
from app.student import bp
from app.student.forms import UploadForm, SolutionStudentSearchForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate, Lesson, Solutions, User, Role, SolutionStatus
from app import db


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    RouteService.validate_role(current_user, Role.STUDENT)
    return redirect(url_for('student.view_courses'))


@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    RouteService.validate_role(current_user, Role.STUDENT)
    return render_template('student/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    RouteService.validate_role_course(current_user, Role.STUDENT, course)
    return render_template('student/course.html', course=course)


@bp.route('<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    RouteService.validate_role(current_user, Role.STUDENT)
    return render_template('student/lesson.html', lesson=Lesson.query.filter_by(id=lesson_id).first())


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(template_id):
    template = ExerciseTemplate.query.filter_by(id=template_id).first()
    RouteService.validate_role_course(current_user, Role.STUDENT, template.get_course())
    form = UploadForm()
    attempts = len(template.get_user_solutions(current_user.id))
    if form.validate_on_submit():
        file = request.files['file']
        filename = secure_filename(file.filename)
        solution = Solutions(user_id=current_user.id, exercise_template_id=template.id, file_path=filename, points=0,
                             ip_address=request.remote_addr, os_info=str(request.user_agent), attempt=attempts,
                             status=SolutionStatus.SEND, send_date=datetime.now(pytz.timezone('Europe/Warsaw')))
        directory = os.path.join(template.get_directory(), current_user.login, str(attempts))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(os.path.join(directory, filename))
        if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
                '.tar'):
            shutil.unpack_archive(os.path.join(directory, filename), directory)
        current_user.solutions.append(solution)
        db.session.commit()
        try:
            ExerciseService.grade(solution)
        except:
            solution.points = 0
            solution.is_active = False
            db.session.commit()
        return redirect(url_for('student.view_lesson', lesson_id=template.lesson.id))
    return render_template('student/exercise.html', template=template, form=form, datetime=datetime.utcnow(),
                           solutions=template.get_user_solutions(current_user.id))


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    RouteService.validate_role(current_user, Role.STUDENT)
    form = SolutionStudentSearchForm()
    form_courses = []
    for course in current_user.courses:
        course_data = (course.name, course.name)
        form_courses.append(course_data)
    form.course.choices = form_courses
    if request.method == 'POST':
        if form.validate_on_submit():
            solutions = ExerciseService.exercise_query(form, current_user.id).all()
            return render_template('student/solutions.html', form=form, solutions=solutions)
    return render_template('student/solutions.html', form=form, solutions=[])


@bp.route('/uploads/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
def download_content(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    RouteService.validate_role_course(current_user, Role.STUDENT, lesson.course)
    return send_from_directory(directory=lesson.get_directory(),
                               filename=lesson.content_pdf_path)


@bp.route('/mysolution/<int:solution_id>/', methods=['GET', 'POST'])
@login_required
def download_solution(solution_id):
    solution = Solutions.query.filter_by(id=solution_id).first()
    RouteService.validate_role_solution(current_user, Role.STUDENT, solution)
    return send_from_directory(directory=solution.get_directory(),
                               filename=solution.file_path)
