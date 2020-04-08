import os
from flask import render_template, url_for, flash, request
from flask_login import login_required

from app.student import bp
from app.admin.forms import UploadForm, CourseForm, TemplateForm, LessonForm, CreateAccountRequestForm
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
    courses = Course.query.all()
    return render_template('student/courses.html', courses=courses)


@bp.route('/course/<string:course_name>')
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    return render_template('student/course.html', course=course)


@bp.route('/<string:course_name>/<int:lesson_id>')
def lesson(course_name, lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    return render_template('student/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/<string:lesson_name>/exercise/<int:template_id>', methods=['GET', 'POST'])
def exercise(course_name, lesson_name, template_id):
    exercise = ExerciseTemplate.query.filter_by(id=template_id).first()
    return render_template('student/exercise.html', template=exercise)


@bp.route('/<string:lesson_name>/<int:user_id>/add_solution', methods=['GET', 'POST'])
def add_solution(lesson_name, user_id):
    form = UploadForm()
    user = User.query.filter_by(id=user_id).first()
    lesson = Lesson.query.filter_by(name=lesson_name).first()
    if form.validate_on_submit():
        solution = UserExercises(name=form.content.data, content=form.content.data, lesson_id=lesson.id)
        user.user_exercises.append(solution)
        db.session.commit()
        return redirect(url_for('student.lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('student/add_solution.html', form=form)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join("/home/michal/uploads/", secure_filename(file.filename)))
    return render_template('upload.html', form=form)

