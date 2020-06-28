import os
import subprocess

from pointer import db
from pointer.models.exercise import Exercise
from pointer.models.solution import Solution


def execute_solution_thread(app, solution_id):
    with app.app_context():
        try:
            solution = Solution.query.filter_by(id=solution_id).first()
            if compile(solution):
                grade(solution)
            else:
                solution.status = solution.Status['COMPILE_ERROR']
                db.session.commit()
        except:
            solution.points = 0
            solution.status = Solution.Status['ERROR']
            db.session.commit()


def execute_solution(solution):
    try:
        if compile(solution):
            grade(solution)
        else:
            solution.status = solution.Status['COMPILE_ERROR']
            db.session.commit()
    except:
        solution.points = 0
        solution.status = Solution.Status['ERROR']
        db.session.commit()


def accept_best_solution(user_id: int, exercise: Exercise):
    user_exercises = Solution.query.filter_by(user_id=user_id, exercise_id=exercise.id).all()
    points, best_solution = 0, None
    for user_exercise in user_exercises:
        if user_exercise.status in [Solution.Status['SEND'],
                                    Solution.Status['ACTIVE']] and user_exercise.points >= points:
            best_solution = user_exercise
            points = best_solution.points
    if best_solution is not None:
        best_solution.status = Solution.Status['ACTIVE']
        user_exercises.remove(best_solution)
    for user_exercise in user_exercises:
        if user_exercise.status not in [Solution.Status['REFUSED'], Solution.Status['RUN_ERROR'],
                                        Solution.Status['COMPILE_ERROR'], Solution.Status['ERROR']]:
            user_exercise.status = Solution.Status['NOT_ACTIVE']
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
        # try:
        #     outs, errs = process.communicate(timeout=15)
        # except subprocess.TimeoutExpired:
        #     process.kill()
        #     outs, errs = process.communicate()
        process.wait(15)
        error_file.close()
        if os.path.getsize(error_file.name) > 0:
            solution.status = Solution.Status['RUN_ERROR']
            break
        elif len(output) == 0:
            solution.points += test.points
        else:
            break
    accept_best_solution(solution.user_id, exercise)
