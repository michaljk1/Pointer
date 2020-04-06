import os
from flask import render_template, url_for, flash, request
from flask_login import logout_user, login_required
from app.main import bp
from app.main.forms import UploadForm, CourseForm, TemplateForm, LessonForm
from werkzeug.utils import secure_filename, redirect
from app.models import Course, ExerciseTemplate, Lesson
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


@bp.route('/addcourse', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_course = Course(name=form.name.data)
            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('main.courses'))
    return render_template('add_course.html', form=form)


@bp.route('/course/<string:course_name>')
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    return render_template('course.html', course=course)


@bp.route('/course/<int:lesson_id>')
def lesson(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    course = Course.query.filter_by(id=lesson.course_id).first()
    return render_template('lesson.html', lesson=lesson, course=course)


@bp.route('/add_lesson/<string:course_name>', methods=['GET', 'POST'])
def add_lesso(course_name):
    form = LessonForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            course = Course.query.filter_by(name=course_name).first()
            new_lesson = Lesson(name=form.name.data, raw_text=form.text_content.data)
            course.lessons.append(new_lesson)
            db.session.commit()
            return redirect(url_for('main.courses'))
    return render_template('add_lesson.html', form=form)


@bp.route('/template/<int:template_id>', methods=['GET', 'POST'])
def template(template_id):
    template = ExerciseTemplate.query.filter_by(id=template_id).first()
    return render_template('template.html', template=template)


@bp.route('/courses', methods=['GET'])
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


@bp.route('/<string:course_name>/<string:lesson_name>/template', methods=['GET', 'POST'])
def add_exercise(course_name, lesson_name):
    course = Course.query.filter_by(name=course_name).first()
    if course is None:
        return redirect(url_for('auth.login'))
    form = TemplateForm()
    if form.validate_on_submit():
        lesson = Lesson.query.filter_by(name=lesson_name).first()
        if lesson is not None:
            exercise_template = ExerciseTemplate(content=form.content.data, lesson_id=lesson.id)
            lesson.exercise_templates.append(exercise_template)
            db.session.commit()
            return redirect(url_for('main.lesson', lesson_id=lesson.id))
    return render_template('add_template.html', form=form)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join("/home/michal/uploads/", secure_filename(file.filename)))
    return render_template('upload.html', form=form)

