import os
import shutil
from datetime import datetime

import pytz
from flask import render_template, url_for, request, send_from_directory
from flask_login import login_required, current_user
from app.services.ExerciseService import ExerciseService
from app.student import bp
from app.student.forms import UploadForm, SolutionStudentSearchForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate, Lesson, UserExercises, User
from app import db


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('student/index.html')


@bp.route('/courses', methods=['GET'])
@login_required
def courses():
    return render_template('student/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
@login_required
def course(course_name):
    return render_template('student/course.html', course=Course.query.filter_by(name=course_name).first())


@bp.route('<int:lesson_id>')
@login_required
def lesson(lesson_id):
    return render_template('student/lesson.html', lesson=Lesson.query.filter_by(id=lesson_id).first())


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
@login_required
def exercise(template_id):
    print(datetime.now(pytz.timezone('Europe/Warsaw')))
    template = ExerciseTemplate.query.filter_by(id=template_id).first()
    form = UploadForm()
    lesson = template.lesson
    attempts = len(UserExercises.query.filter_by(user_id=current_user.id, exercise_template_id=template.id).all())
    if form.validate_on_submit():
        file = request.files['file']
        filename = secure_filename(file.filename)
        solution = UserExercises(user_id=current_user.id, exercise_template_id=template.id, file_path=filename,
                                 os_info=str(request.user_agent), attempt=attempts)
        directory = os.path.join(template.get_directory(), current_user.login, str(attempts))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(os.path.join(directory, filename))
        if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
                '.tar'):
            shutil.unpack_archive(os.path.join(directory, filename), directory)
        current_user.user_exercises.append(solution)
        db.session.commit()
        try:
            ExerciseService.grade(solution)
        except:
            solution.points = 0
            solution.is_active = False
            db.session.commit()
        return redirect(url_for('student.lesson', lesson_id=lesson.id))
    return render_template('student/exercise.html', template=template, form=form, datetime=datetime.utcnow(), solutions=template.get_user_solutions(current_user.id))


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def solutions():
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


@bp.route('/uploads/<int:lesson_id>/<path:filename>', methods=['GET', 'POST'])
@login_required
def download(lesson_id, filename):
    return send_from_directory(directory=Lesson.query.filter_by(id=lesson_id).first().get_directory(),
                               filename=filename)
