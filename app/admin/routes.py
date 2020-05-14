import os
import string
import random

from flask import render_template, url_for, flash, request, current_app
from flask_login import logout_user, login_required, current_user
from app.admin import bp
from app.admin.forms import CourseForm, TemplateForm, LessonForm, CreateAccountRequestForm, SolutionsForm, SolutionForm
from werkzeug.utils import redirect, secure_filename
from app.models import Course, ExerciseTemplate, Lesson, User, UserExercises
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
    return render_template('admin/add_student.html', form=form, course=course)


@bp.route('/create_account/<token>', methods=['GET', 'POST'])
def create_account(token):
    return render_template('admin/create_account.html')


@bp.route('/courses', methods=['GET'])
def courses():
    return render_template('admin/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    return render_template('admin/course.html', course=course)


@bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # TODO unique link
            new_course = Course(name=form.name.data,
                                link=''.join(random.choice(string.ascii_lowercase) for i in range(15)))
            current_user.courses.append(new_course)
            os.makedirs(new_course.get_directory())
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
            file = request.files['pdf_content']
            filename = secure_filename(file.filename)
            lesson_name = form.name.data
            new_lesson = Lesson(name=lesson_name, content_pdf_path=filename, content_url=form.content_url.data,
                                raw_text=form.text_content.data)
            course = Course.query.filter_by(name=course_name).first()
            directory = os.path.join(course.get_directory(), lesson_name)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(directory, filename))
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


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
def exercise(template_id):
    form = SolutionsForm()
    solutions = UserExercises.query.filter_by(exercise_template_id=template_id).all()
    exercise = ExerciseTemplate.query.filter_by(id=template_id).first()
    for solution in solutions:
        solution_form = SolutionForm()
        solution_form.accept = solution.is_approved
        solution_form.points = solution.points
        solution_form.attempt = solution.attempt
        solution_form.file = solution.file_path
        form.solutions.append_entry(solution_form)
    if request.method == 'POST':
        for single_form in form.solutions.data:
            for solution in solutions:
                if solution.attempt == single_form['attempt'] and solution.file_path == single_form['file'] \
                        and single_form['csrf_token'] == '':
                    solution.is_approved = single_form['accept']
                    solution.points = single_form['points']
                    break
        db.session.commit()
        flash('Zapisano zmiany')
        return redirect(url_for('admin.exercise', template_id=exercise.id))
    return render_template('admin/exercise.html', template=exercise, form=form)


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
def add_exercise(course_name, lesson_name):
    form = TemplateForm()
    if form.validate_on_submit():
        lesson = Lesson.query.filter_by(name=lesson_name).first()
        if lesson is not None:
            exercise_template = ExerciseTemplate(name=form.name.data, content=form.content.data, lesson_id=lesson.id,
                                                 max_attempts=form.max_attempts.data, max_points=form.max_points.data)
            lesson.exercise_templates.append(exercise_template)
            db.session.commit()
            return redirect(url_for('admin.lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('admin/add_template.html', form=form)
