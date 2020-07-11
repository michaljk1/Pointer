import os
from threading import Thread
from flask import render_template, url_for, request, send_from_directory, current_app, abort
from flask_login import login_required, current_user

from pointer import db
from pointer.DefaultUtil import get_current_date, unpack_file, get_offset_aware
from pointer.models.solution import Solution
from pointer.services.ExerciseService import execute_solution_thread
from pointer.services.QueryService import get_filtered_by_status, exercise_student_query
from pointer.services.RouteService import validate_role, validate_role_course, validate_role_solution, validate_exercise
from pointer.student import bp
from pointer.student.StudentUtil import can_send_solution
from pointer.student.student_forms import UploadForm, SolutionStudentSearchForm, StudentSolutionForm
from werkzeug.utils import secure_filename, redirect
from pointer.models.usercourse import Course, role
from pointer.models.exercise import Exercise
from pointer.models.lesson import Lesson
from pointer.models.statistics import Statistics


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, role['STUDENT'])
    return redirect(url_for('student.view_courses'))


@bp.route('/courses', methods=['GET'])
@login_required
def view_courses():
    validate_role(current_user, role['STUDENT'])
    return render_template('student/courses.html', courses=current_user.courses)


@bp.route('/course/<string:course_name>')
@login_required
def view_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['STUDENT'], course)
    return render_template('student/course.html', course=course)


@bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_role_course(current_user, role['STUDENT'], lesson.course)
    return render_template('student/lesson.html', lesson=lesson)


@bp.route('/solution/<int:solution_id>')
@login_required
def view_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    if solution not in current_user.solutions:
        abort(404)
    validate_role_course(current_user, role['STUDENT'], solution.get_course())
    form = StudentSolutionForm(obj=solution, student_status=solution.get_student_status(),
                               student_points=solution.get_student_points(), send_date_str=str(solution.send_date))
    return render_template('student/solution.html', solution=solution, form=form)


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise(exercise)
    validate_role_course(current_user, role['STUDENT'], exercise.get_course())
    solutions = sorted(exercise.get_student_solutions(current_user.id), key=lambda sol: sol.send_date, reverse=True)
    send_solution = can_send_solution(solutions)
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['file']
        filename = secure_filename(file.filename)
        solution = Solution(file_path=filename, points=0, ip_address=request.remote_addr,
                            os_info=str(request.user_agent), attempt=(1 + len(solutions)),
                            status=Solution.Status['SEND'], send_date=get_current_date())
        exercise.solutions.append(solution)
        current_user.solutions.append(solution)
        solution_directory = solution.get_directory()
        os.makedirs(solution_directory)
        file.save(os.path.join(solution_directory, filename))
        unpack_file(filename, solution_directory)
        db.session.commit()
        Thread(target=execute_solution_thread, args=(current_app._get_current_object(), solution.id)).start()
        return redirect(url_for('student.view_exercise', exercise_id=exercise.id))
    return render_template('student/exercise.html', exercise=exercise, form=form, send_solution=send_solution,
                           solutions=solutions)


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, role['STUDENT'])
    form, solutions = SolutionStudentSearchForm(), []
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        all_solutions = exercise_student_query(form=form, courses=current_user.get_course_names(),
                                               student_id=current_user.id).all()
        solutions = sorted(get_filtered_by_status(all_solutions, form.status.data), key=lambda sol: sol.send_date,
                           reverse=True)
    return render_template('student/solutions.html', form=form, solutions=solutions)


@bp.route('/statistics')
@login_required
def view_statistics():
    validate_role(current_user, role['STUDENT'])
    statistics_list = []
    for course in current_user.courses:
        statistics_list.append(Statistics(course=course, user=current_user))
    return render_template('student/statistics.html', statisticsList=statistics_list)


@bp.route('/uploads/<int:lesson_id>/', methods=['GET', 'POST'])
@login_required
def download_content(lesson_id):
    lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_role_course(current_user, role['STUDENT'], lesson.course)
    return send_from_directory(directory=lesson.get_directory(), filename=lesson.content_pdf_path)


@bp.route('/mysolution/<int:solution_id>/', methods=['GET', 'POST'])
@login_required
def download_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_role_solution(current_user, role['STUDENT'], solution)
    return send_from_directory(directory=solution.get_directory(), filename=solution.file_path)
