import os
import subprocess

from app import db
from app.models import Solution, Exercise


def execute_solution_thread(app, solution):
    with app.app_context():
        try:
            if compile(solution):
                grade(solution)
            else:
                solution.status = solution.solutionStatus['COMPILE_ERROR']
                db.session.commit()
        except:
            solution.points = 0
            solution.status = Solution.solutionStatus['ERROR']
            solution.is_active = False
            db.session.commit()


def execute_solution(solution):
    try:
        if compile(solution):
            grade(solution)
        else:
            solution.status = solution.solutionStatus['COMPILE_ERROR']
            db.session.commit()
    except:
        solution.points = 0
        solution.status = Solution.solutionStatus['ERROR']
        solution.is_active = False
        db.session.commit()


def accept_best_solution(user_id: int, exercise: Exercise):
    user_exercises = Solution.query.filter_by(user_id=user_id, exercise_id=exercise.id).all()
    points, best_solution = 0, None
    for user_exercise in user_exercises:
        if user_exercise.status in [Solution.solutionStatus['SEND'],
                                    Solution.solutionStatus['ACTIVE']] and user_exercise.points >= points:
            best_solution = user_exercise
            points = best_solution.points
    if best_solution is not None:
        best_solution.status = Solution.solutionStatus['ACTIVE']
        user_exercises.remove(best_solution)
    for user_exercise in user_exercises:
        if user_exercise.status not in [Solution.solutionStatus['REFUSED'], Solution.solutionStatus['RUN_ERROR'],
                                        Solution.solutionStatus['REFUSED']]:
            user_exercise.status = Solution.solutionStatus['NOT_ACTIVE']
    db.session.commit()


def compile(solution):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    compile_command = solution.exercise.compile_command
    error_file = open(os.path.join(solution.get_directory(), 'compilerror.txt'), 'w+')
    if len(compile_command.split()) > 0:
        bash_command = dir_path + '/compile.sh ' + solution.get_directory() + ' ' + compile_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, stderr=error_file)
        process.wait()
        error_file.close()
        if os.path.getsize(error_file.name) > 0:
            return False
        else:
            return True


def grade(solution):
    exercise = solution.exercise
    program_name = solution.file_path
    run_command = exercise.run_command
    dir_path = os.path.dirname(os.path.realpath(__file__))
    solution.points = 0
    for test in exercise.tests.all():
        name = 'error_test_run' + str(test.id) + '.txt'
        error_file = open(os.path.join(solution.get_directory(), name), 'w+')
        test_dir = test.get_directory()
        input_name, output_name = test_dir + '/' + test.input_name, test_dir + '/' + test.output_name
        bash_command = dir_path + '/run.sh ' + solution.get_directory() + ' ' + program_name + ' ' + input_name + ' ' + output_name + ' ' + run_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, stderr=error_file)
        output, error = process.communicate()
        process.wait()
        error_file.close()
        if os.path.getsize(error_file.name) > 0:
            solution.status = Solution.solutionStatus['RUN_ERROR']
            break
        elif len(output) == 0:
            solution.points += test.points
        else:
            break
    accept_best_solution(solution.user_id, exercise)
