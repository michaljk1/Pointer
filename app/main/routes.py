import os
from flask import render_template, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.main import bp
from app.main.forms import UploadForm, CourseForm, TemplateForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate
from app import db


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/course', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_course = Course(name=form.name.data)
            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('main.courses'))
    return render_template('addcourse.html', form=form)


@bp.route('/course/<string:course_name>', methods=['GET', 'POST'])
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    return render_template('course.html', course=course)


@bp.route('/courses', methods=['GET'])
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


@bp.route('/<string:course_name>/template', methods=['GET', 'POST'])
def add_exercise(course_name):
    course = Course.query.filter_by(name=course_name).first()
    if course is None:
        return redirect(url_for('auth.login'))
    form = TemplateForm()
    if form.validate_on_submit():
        exercise_template = ExerciseTemplate(content=form.content.data, course_id=course.id)
        db.session.add(exercise_template)
        db.session.commit()
    return render_template('template.html', form=form)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join("/home/michal/uploads/", secure_filename(file.filename)))
    return render_template('upload.html', form=form)

