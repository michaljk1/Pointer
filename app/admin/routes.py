import os
import string
import random

from flask import render_template, url_for, flash, request, abort
from flask_login import logout_user, login_required, current_user
from app.admin import bp
from app.admin.forms import CourseForm, TemplateForm, LessonForm, CreateAccountRequestForm, SolutionForm, \
    SolutionAdminSearchForm
from werkzeug.utils import redirect, secure_filename
from app.models import Course, ExerciseTemplate, Lesson, User, UserExercises, Role
from app import db
from app.services.ExerciseService import ExerciseService
from app.services.RouteService import RouteService


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    RouteService.validate_role(current_user, Role.ADMIN)
    return render_template('admin/index.html')


@bp.route('/logout')
def logout():
    RouteService.validate_role(current_user, Role.ADMIN)
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/<string:course_name>/add_student', methods=['GET', 'POST'])
def add_student(course_name):
    RouteService.validate_role(current_user, Role.ADMIN)
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
def view_courses():
    RouteService.validate_role(current_user, Role.ADMIN)
    return render_template('admin/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    RouteService.validate_role_course(current_user, Role.ADMIN, course)
    return render_template('admin/course.html', course=course)


@bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    RouteService.validate_role(current_user, Role.ADMIN)
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_course = Course(name=form.name.data,
                            link=''.join(random.choice(string.ascii_lowercase) for i in range(25)))
        current_user.courses.append(new_course)
        os.makedirs(new_course.get_directory())
        db.session.commit()
        flash('Dodano kurs')
        return redirect(url_for('admin.view_courses'))
    return render_template('admin/add_course.html', form=form)


@bp.route('/<string:course_name>/<int:lesson_id>')
def view_lesson(course_name, lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    RouteService.validate_role_course(current_user, Role.ADMIN, lesson.course)
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
def add_lesson(course_name):
    course = Course.query.filter_by(name=course_name).first()
    RouteService.validate_role_course(current_user, Role.ADMIN, course)
    form = LessonForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['pdf_content']
            filename = secure_filename(file.filename)
            lesson_name = form.name.data
            new_lesson = Lesson(name=lesson_name, content_pdf_path=filename, content_url=form.content_url.data,
                                raw_text=form.text_content.data)
            directory = os.path.join(course.get_directory(), lesson_name.replace(" ", "_"))
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(directory, filename))
            course.lessons.append(new_lesson)
            db.session.commit()
            return redirect(url_for('admin.view_lesson', lesson_id=new_lesson.id, course_name=course.name))
    return render_template('admin/add_lesson.html', form=form)


@bp.route('/exercise/<int:template_id>', methods=['GET', 'POST'])
def view_exercise(template_id):
    exercise = ExerciseTemplate.query.filter_by(id=template_id).first()
    RouteService.validate_role_course(current_user, Role.ADMIN, exercise.lesson.course)
    solutions = UserExercises.query.filter_by(exercise_template_id=template_id, is_active=True).all()
    return render_template('admin/exercise.html', template=exercise, solutions=solutions)


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
def add_exercise(course_name, lesson_name):
    course = Course.query.filter_by(name=course_name).first()
    lesson = course.get_lesson_by_name(lesson_name)
    RouteService.validate_exists(lesson)
    RouteService.validate_role_course(current_user, Role.ADMIN, course)
    form = TemplateForm()
    if form.validate_on_submit():
        input = request.files['input']
        input_name = secure_filename(input.filename)
        output = request.files['output']
        output_name = secure_filename(output.filename)
        exercise_name = form.name.data
        exercise_template = ExerciseTemplate(name=exercise_name, content=form.content.data, lesson_id=lesson.id,
                                             max_attempts=form.max_attempts.data, max_points=form.max_points.data,
                                             input_name=input_name, output_name=output_name,
                                             compile_command=form.compile_command.data, end_date=form.end_date.data,
                                             run_command=form.run_command.data, program_name=form.program_name.data)
        lesson.exercise_templates.append(exercise_template)
        directory = os.path.join(lesson.get_directory(), exercise_name.replace(" ", "_"))
        if not os.path.exists(directory):
            os.makedirs(directory)
        input.save(os.path.join(directory, input_name))
        output.save(os.path.join(directory, output_name))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', course_name=lesson.course.name, lesson_id=lesson.id))
    return render_template('admin/add_template.html', form=form)


@bp.route('/solutions', methods=['GET', 'POST'])
def view_solutions():
    RouteService.validate_role(current_user, Role.ADMIN)
    form = SolutionAdminSearchForm()
    form_courses = []
    for course in current_user.courses:
        course_data = (course.name, course.name)
        form_courses.append(course_data)
    form.course.choices = form_courses
    if request.method == 'POST':
        if form.validate_on_submit():
            solutions = ExerciseService.exercise_query(form).all()
            return render_template('admin/solutions.html', form=form, solutions=solutions)
    return render_template('admin/solutions.html', form=form, solutions=[])


@bp.route('/solution/<int:solution_id>', methods=['GET', 'POST'])
def view_solution(solution_id):
    solution = UserExercises.query.filter_by(id=solution_id).first()
    RouteService.validate_exists(solution)
    RouteService.validate_role_course(current_user, Role.ADMIN, solution.template.lesson.course)
    solution_form = SolutionForm(obj=solution, email=solution.author.email)
    if request.method == 'POST':
        solution.admin_refused = solution_form.admin_refused.data
        solution.points = solution_form.points.data
        db.session.commit()
        ExerciseService.accept_best_solution(solution.user_id, solution.template)
        flash('Zapisano zmiany')
        return render_template('admin/solution.html', form=solution_form)
    return render_template('admin/solution.html', form=solution_form)
