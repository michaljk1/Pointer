import os
import subprocess

from app import db
from app.models import Solutions, User, Course, Lesson, Exercise, SolutionStatus


def accept_best_solution(user_id, exercise):
    user_exercises = Solutions.query.filter_by(user_id=user_id, exercise_id=exercise.id).all()
    points = 0
    best_solution = None
    for user_exercise in user_exercises:
        if user_exercise.status != SolutionStatus.REFUSED and user_exercise.points >= points:
            best_solution = user_exercise
            points = best_solution.points
    if best_solution is not None:
        best_solution.status = SolutionStatus.ACTIVE
        user_exercises.remove(best_solution)
    for user_exercise in user_exercises:
        if user_exercise.status != SolutionStatus.REFUSED:
            user_exercise.status = SolutionStatus.SEND
    db.session.commit()


def compile(solution):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    compile_command = solution.exercise.compile_command
    bash_command = dir_path + '/compile.sh ' + solution.get_directory() + ' ' + compile_command
    subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)


def grade(solution):
    exercise = solution.exercise
    program_name = solution.file_path
    run_command = exercise.run_command
    dir_path = os.path.dirname(os.path.realpath(__file__))
    solution.points = 0
    for test in exercise.tests.all():
        test_dir = test.get_directory()
        input_name = test_dir + '/' + test.input_name
        output_name = test_dir + '/' + test.output_name
        bash_command = dir_path + '/run.sh ' + solution.get_directory() + ' ' + program_name + ' ' + input_name + ' ' + output_name + ' ' + run_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if len(output) == 0:
            solution.points += test.points
    accept_best_solution(solution.user_id, exercise)


def exercise_query(form, user_id=None):
    query = db.session.query(Solutions).select_from(Solutions, User, Course, Lesson, Exercise). \
        join(User, User.id == Solutions.user_id). \
        join(Exercise, Solutions.exercise_id == Exercise.id). \
        join(Lesson, Lesson.id == Exercise.lesson_id). \
        join(Course, Course.id == Lesson.course_id)

    if form.status.data != SolutionStatus.ALL:
        query = query.filter(Solutions.status == form.status.data)
    if form.points_from.data is not None:
        query = query.filter(Solutions.points >= form.points_from.data)
    if form.points_to.data is not None:
        query = query.filter(Solutions.points <= form.points_to.data)
    if not len(form.course.data) == 0:
        query = query.filter(Course.name == form.course.data)
    if not len(form.lesson.data) == 0:
        query = query.filter(Lesson.name == form.lesson.data)
    # Admin is able to search by name and surname, student can only view his solutions
    from app.admin.forms import SolutionAdminSearchForm
    if isinstance(form, SolutionAdminSearchForm):
        if not len(form.surname.data) == 0:
            query = query.filter(User.surname == form.surname.data)
        if not len(form.name.data) == 0:
            query = query.filter(User.name == form.name.data)
    else:
        query = query.filter(User.id == user_id)
    if not len(form.exercise.data) == 0:
        query = query.filter(Exercise.name == form.exercise.data)
    return query
