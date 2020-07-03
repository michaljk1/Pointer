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
            solution.status = Solution.Status['NOT_ACTIVE']
            db.session.commit()
        except:
            solution.status = Solution.Status['ERROR']
            db.session.commit()


def compile(solution: Solution):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    compile_command = solution.exercise.compile_command
    error_file = open(os.path.join(solution.get_directory(), 'compilerror.txt'), 'w+')
    if len(compile_command.split()) > 0:
        bash_command = dir_path + '/compile.sh ' + solution.get_directory() + ' ' + compile_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, stderr=error_file)
        process.wait()
        error_file.close()
        if os.path.getsize(error_file.name) > 0:
            with open(error_file.name) as f:
                solution.error_msg = f.read()
            solution.status = Solution.Status['COMPILE_ERROR']
            return False
        else:
            return True
    else:
        return True


def grade(solution: Solution):
    exercise = solution.exercise
    program_name = exercise.program_name
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
        try:
            outs = process.communicate(timeout=solution.exercise.timeout)[0]
            error_file.close()
            if os.path.getsize(error_file.name) > 0:
                solution.status = Solution.Status['RUN_ERROR']
                with open(error_file.name) as f:
                    solution.error_msg = f.read().split("run.sh")[1][2:].split("$RUN_COMMAND")[0]
                break
            elif len(outs) == 0:
                solution.points += test.points
            else:
                break
        except subprocess.TimeoutExpired:
            process.kill()