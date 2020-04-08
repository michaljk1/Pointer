import os
from flask import render_template, url_for, flash, request
from app.student import bp
from app.admin.forms import UploadForm, CourseForm, TemplateForm, LessonForm, CreateAccountRequestForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate, Lesson, User, UserExercises
from app import db


@bp.route('/courses', methods=['GET'])
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


@bp.route('/course/<string:course_name>')
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    return render_template('course.html', course=course)


@bp.route('/<string:course_name>/<int:lesson_id>')
def lesson(course_name, lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    return render_template('lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/<string:lesson_name>/<int:user_id>/add_exercise', methods=['GET', 'POST'])
def add_solution(course_name, lesson_name, user_id):
    form = TemplateForm()
    user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        lesson = Lesson.query.filter_by(name=lesson_name).first()
        if lesson is not None:
            solution = UserExercises(name=form.content.data, content=form.content.data, lesson_id=lesson.id)
            user.user_exercises.append(solution)
            db.session.commit()
            return redirect(url_for('user.lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('add_solution.html', form=form)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join("/home/michal/uploads/", secure_filename(file.filename)))
    return render_template('upload.html', form=form)

