import os
from flask import render_template, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user

from app.student import bp
from app.admin.forms import UploadForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate, Lesson, User, UserExercises
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
    course = Course.query.filter_by(name=course_name).first()
    return render_template('student/course.html', course=course)


@bp.route('<int:lesson_id>')
def lesson(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    return render_template('student/lesson.html', lesson=lesson)


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
def exercise(template_id):
    exercise = ExerciseTemplate.query.filter_by(id=template_id).first()
    return render_template('student/exercise.html', template=exercise)


@bp.route('/<string:lesson_name>/add_solution', methods=['GET', 'POST'])
def add_solution(lesson_name):
    form = UploadForm()
    lesson = Lesson.query.filter_by(name=lesson_name).first()
    if form.validate_on_submit():
        # solution = UserExercises(name=form.content.data, content=form.content.data, lesson_id=lesson.id)
        file = request.files['file']
        file.save(os.path.join("/home/", secure_filename(file.filename)))
        # current_user.user_exercises.append(solution)
        # db.session.commit()
        return redirect(url_for('student.lesson', lesson_id=lesson.id))
    return render_template('student/add_solution.html', form=form)


@bp.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.instance_path, 'uploads')
    return send_from_directory(directory=uploads, filename=filename)

