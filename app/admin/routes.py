import os
from flask import render_template, url_for, flash, request, current_app
from flask_login import logout_user, login_required, current_user
from app.admin import bp
from app.admin.forms import CourseForm, TemplateForm, LessonForm, CreateAccountRequestForm
from werkzeug.utils import redirect, secure_filename
from app.models import Course, ExerciseTemplate, Lesson, User
from app import db


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('admin/index.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
def add_student(course_name):
    form = CreateAccountRequestForm()
    course = Course.query.filter_by(name=course_name).first()
    users = []
    for user in User.query.all():
        data = (user.email, user.email)
        users.append(data)
    form.email.choices = users
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
        db.session.commit()
        flash('Dodano studenta')
    return render_template('email/create_account_request.html', form=form)


@bp.route('/create_account/<token>', methods=['GET', 'POST'])
def create_account(token):
    return render_template('admin/create_account.html')


@bp.route('/courses', methods=['GET'])
def courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)


@bp.route('/course/<string:course_name>')
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    return render_template('admin/course.html', course=course)


@bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_course = Course(name=form.name.data)
            current_user.courses.append(new_course)
            db.session.commit()
            flash('Dodano kurs')
            return redirect(url_for('admin.courses'))
    return render_template('admin/add_course.html', form=form)


@bp.route('/<string:course_name>/<int:lesson_id>')
def lesson(course_name, lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
def add_lesson(course_name):
    form = LessonForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            course = Course.query.filter_by(name=course_name).first()
            file = request.files['pdf_content']
            uploads_dir = os.path.join(current_app.instance_path, 'uploads')
            filename = secure_filename(file.filename)
            file.save(os.path.join(uploads_dir, filename))
            new_lesson = Lesson(name=form.name.data, content_pdf_path=filename, content_url=form.content_url.data,
                                raw_text=form.text_content.data)
            course.lessons.append(new_lesson)
            db.session.commit()
            return redirect(url_for('admin.lesson', lesson_id=new_lesson.id, course_name=course.name))
    return render_template('admin/add_lesson.html', form=form)


# @bp.route('/<string:course_name>/invite_student', methods=['GET', 'POST'])
# def invite_student(course_name):
#     form = LessonForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             course = Course.query.filter_by(name=course_name).first()
#             new_lesson = Lesson(name=form.name.data, content_url=form.url_content.data, raw_text=form.text_content.data)
#             course.lessons.append(new_lesson)
#             db.session.commit()
#             return redirect(url_for('admin.lesson', lesson_id=new_lesson.id, course_name=course.name))
#     return render_template('admin/add_lesson.html', form=form)


@bp.route('/<string:course_name>/<string:lesson_name>/exercise/<int:template_id>', methods=['GET', 'POST'])
def exercise(course_name, lesson_name, template_id):
    exercise = ExerciseTemplate.query.filter_by(id=template_id).first()
    return render_template('admin/exercise.html', template=exercise)


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
def add_exercise(course_name, lesson_name):
    form = TemplateForm()
    if form.validate_on_submit():
        lesson = Lesson.query.filter_by(name=lesson_name).first()
        if lesson is not None:
            exercise_template = ExerciseTemplate(name=form.content.data, content=form.content.data, lesson_id=lesson.id)
            lesson.exercise_templates.append(exercise_template)
            db.session.commit()
            return redirect(url_for('admin.lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('admin/add_template.html', form=form)
