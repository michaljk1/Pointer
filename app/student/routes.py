import os
from flask import render_template, url_for, request, send_from_directory
from flask_login import login_required, current_user
from app.services.ExerciseService import ExerciseService
from app.student import bp
from app.admin.forms import UploadForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate, Lesson, UserExercises
from app import db


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('student/index.html')


@bp.route('/courses', methods=['GET'])
def courses():
    return render_template('student/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
def course(course_name):
    return render_template('student/course.html', course=Course.query.filter_by(name=course_name).first())


@bp.route('<int:lesson_id>')
def lesson(lesson_id):
    return render_template('student/lesson.html', lesson=Lesson.query.filter_by(id=lesson_id).first())


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
def exercise(template_id):
    return render_template('student/exercise.html', template=ExerciseTemplate.query.filter_by(id=template_id).first())


@bp.route('/<string:lesson_name>/<string:exercise_name>/add_solution', methods=['GET', 'POST'])
def add_solution(lesson_name, exercise_name):
    form = UploadForm()
    lesson = Lesson.query.filter_by(name=lesson_name).first()
    exercise = ExerciseTemplate.query.filter_by(name=exercise_name).first()
    attempt = len(UserExercises.query.filter_by(user_id=current_user.id, exercise_template_id=exercise.id).all())

    if form.validate_on_submit():
        file = request.files['file']

        filename = secure_filename(file.filename)
        solution = UserExercises(user_id=current_user.id, exercise_template_id=exercise.id, file_path=filename,
                                 os_info=str(request.user_agent), attempt=attempt)
        directory = os.path.join(exercise.get_directory(), current_user.login, str(attempt))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(os.path.join(directory, filename))
        current_user.user_exercises.append(solution)
        db.session.commit()
        try:
            ExerciseService.grade(solution)
        except:
            solution.points = 0
            solution.is_approved = False
            db.session.commit()
        return redirect(url_for('student.lesson', lesson_id=lesson.id))
    return render_template('student/add_solution.html', form=form)


@bp.route('/uploads/<int:lesson_id>/<path:filename>', methods=['GET', 'POST'])
def download(lesson_id, filename):
    return send_from_directory(directory=Lesson.query.filter_by(id=lesson_id).first().get_directory(), filename=filename)
