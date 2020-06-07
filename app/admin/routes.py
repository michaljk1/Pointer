import os
import string
import random

from flask import render_template, url_for, flash, request, current_app, abort, session
from flask_login import logout_user, login_required, current_user
from app.admin import bp
from app.admin.forms import CourseForm, TemplateForm, LessonForm, CreateAccountRequestForm, SolutionForm, \
    SolutionSearchForm
from werkzeug.utils import redirect, secure_filename
from app.models import Course, ExerciseTemplate, Lesson, User, UserExercises
from app import db
from app.services.ExerciseService import ExerciseService


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    if not current_user.is_admin():
        abort(404)
    return render_template('admin/index.html')


@bp.route('/logout')
def logout():
    if not current_user.is_admin():
        abort(404)
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
def add_student(course_name):
    if not current_user.is_admin():
        abort(404)
    form = CreateAccountRequestForm()
    course = Course.query.filter_by(name=course_name).first()
    users = []
    for user in User.query.filter(~User.courses.any(name=course.name)).all():
        data = (user.email, user.email)
        users.append(data)
    form.email.choices = users
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.courses.append(course)
        db.session.commit()
        flash('Dodano studenta')
    return render_template('admin/add_student.html', form=form, course=course)


@bp.route('/courses', methods=['GET'])
def courses():
    if not current_user.is_admin():
        abort(404)
    return render_template('admin/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
def course(course_name):
    if not current_user.is_admin():
        abort(404)
    course = Course.query.filter_by(name=course_name).first()
    return render_template('admin/course.html', course=course)


@bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if not current_user.is_admin():
        abort(404)
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit():
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
    if not current_user.is_admin():
        abort(404)
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
def add_lesson(course_name):
    if not current_user.is_admin():
        abort(404)
    form = LessonForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['pdf_content']
            filename = secure_filename(file.filename)
            lesson_name = form.name.data
            new_lesson = Lesson(name=lesson_name, content_pdf_path=filename, content_url=form.content_url.data,
                                raw_text=form.text_content.data)
            course = Course.query.filter_by(name=course_name).first()
            directory = os.path.join(course.get_directory(), lesson_name.replace(" ", ""))
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(directory, filename))
            course.lessons.append(new_lesson)
            db.session.commit()
            return redirect(url_for('admin.lesson', lesson_id=new_lesson.id, course_name=course.name))
    return render_template('admin/add_lesson.html', form=form)


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
def exercise(template_id):
    if not current_user.is_admin():
        abort(404)
    exercise = ExerciseTemplate.query.filter_by(id=template_id).first()
    solutions = UserExercises.query.filter_by(exercise_template_id=template_id, is_active=True).all()
    return render_template('admin/exercise.html', template=exercise, solutions=solutions)


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
def add_exercise(course_name, lesson_name):
    if not current_user.is_admin():
        abort(404)
    form = TemplateForm()
    if form.validate_on_submit():
        lesson = Lesson.query.filter_by(name=lesson_name).first()
        if lesson is not None:
            input = request.files['input']
            input_name = secure_filename(input.filename)
            output = request.files['output']
            output_name = secure_filename(output.filename)
            exercise_name = form.name.data
            exercise_template = ExerciseTemplate(name=exercise_name, content=form.content.data, lesson_id=lesson.id,
                                                 max_attempts=form.max_attempts.data, max_points=form.max_points.data,
                                                 input_name=input_name, output_name=output_name,
                                                 compile_command=form.compile_command.data,
                                                 run_command=form.run_command.data)
            lesson.exercise_templates.append(exercise_template)
            directory = os.path.join(lesson.get_directory(), exercise_name.replace(" ", ""))
            if not os.path.exists(directory):
                os.makedirs(directory)
            input.save(os.path.join(directory, input_name))
            output.save(os.path.join(directory, output_name))
            db.session.commit()
            return redirect(url_for('admin.lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('admin/add_template.html', form=form)


@bp.route('/solutions', methods=['GET', 'POST'])
def solutions():
    if not current_user.is_admin():
        abort(404)
    form = SolutionSearchForm()
    form_courses = []
    for course in current_user.courses:
        course_data = (course.name, course.name)
        form_courses.append(course_data)
    form.course.choices = form_courses
    if request.method == 'POST':
        if form.validate_on_submit():
            query = db.session.query(UserExercises).select_from(UserExercises, User, Course, Lesson, ExerciseTemplate). \
                join(User, User.id == UserExercises.user_id).join(ExerciseTemplate, UserExercises.exercise_template_id == ExerciseTemplate.id). \
                join(Lesson, Lesson.id == ExerciseTemplate.lesson_id).filter(
                UserExercises.is_active == form.is_active.data,
                UserExercises.admin_refused == form.admin_refused.data)

            if form.points_from.data is not None:
                query = query.filter(UserExercises.points >= form.points_from.data)
            if form.points_to.data is not None:
                query = query.filter(UserExercises.points <= form.points_to.data)
            if not len(form.name.data) == 0:
                query = query.filter(User.name == form.name.data)
            if not len(form.surname.data) == 0:
                query = query.filter(User.surname == form.surname.data)
            if not len(form.course.data) == 0:
                query = query.filter(Course.name == form.course.data)
            if not len(form.lesson.data) == 0:
                query = query.filter(Lesson.name == form.lesson.data)
            if not len(form.exercise_name.data) == 0:
                query = query.filter(ExerciseTemplate.name == form.exercise_name.data)

            solutions = query.all()
            return render_template('admin/solutions.html', form=form, solutions=solutions)
    return render_template('admin/solutions.html', form=form, solutions=[])


@bp.route('/solution/<int:solution_id>', methods=['GET', 'POST'])
def solution(solution_id):
    if not current_user.is_admin():
        abort(404)
    solution = UserExercises.query.filter_by(id=solution_id).first()
    solution_form = SolutionForm(obj=solution, email=solution.author.email)
    if request.method == 'POST':
        solution.points = solution_form.points.data
        solution.admin_refused = solution_form.admin_refused.data
        solution.points = solution_form.points.data
        db.session.commit()
        ExerciseService.accept_best_solution(solution.user_id, solution.template)
        flash('Zapisano zmiany')
        return render_template('admin/solution.html', form=solution_form)
    return render_template('admin/solution.html', form=solution_form)
