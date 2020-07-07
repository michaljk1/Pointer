import os
import subprocess

from pointer import db
from pointer.models.solution import Solution
import resource


def execute_solution_thread(app, solution_id):
    with app.app_context():
        try:
            solution = Solution.query.filter_by(id=solution_id).first()
            if prepare_compilation(solution):
                grade(solution)
            if solution.status == Solution.Status['SEND']:
                solution.status = Solution.Status['NOT_ACTIVE']
            db.session.commit()
        except:
            solution.status = Solution.Status['ERROR']
            db.session.commit()


def prepare_compilation(solution):
    compile_command = solution.exercise.compile_command
    if len(compile_command.split()) > 0:
        return execute_compilation(solution, compile_command)
    else:
        return True


def execute_compilation(solution: Solution, compile_command: str):
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'compile.sh')
    error_file = open(os.path.join(solution.get_directory(), 'compile_error.txt'), 'w+')
    bash_command = [script_path, solution.get_directory(), compile_command]
    process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=error_file)
    process.wait()
    error_file.close()
    if os.path.getsize(error_file.name) > 0:
        with open(error_file.name) as f:
            solution.error_msg = f.read()
        solution.status = Solution.Status['COMPILE_ERROR']
        return False
    else:
        return True


def grade(solution: Solution):
    exercise = solution.exercise
    program_name, run_command = exercise.program_name, exercise.run_command
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run.sh')
    for test in exercise.tests.all():
        name = 'error_test_run' + str(test.id) + '.txt'
        error_file = open(os.path.join(solution.get_directory(), name), 'w+')
        bash_command = [script_path, solution.get_directory(), program_name, test.get_input_path(),
                        test.get_output_path(), run_command]
        process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=error_file)
        # , preexec_fn=(lambda x: resource.setrlimit(resource.RLIMIT_AS,(x * 1024 * 1024, resource.RLIM_INFINITY))))
        try:
            outs = process.communicate(timeout=solution.exercise.timeout)[0]
            error_file.close()
            if os.path.getsize(error_file.name) > 0:
                solution.status = Solution.Status['TEST_ERROR']
                with open(error_file.name) as f:
                    solution.error_msg = f.read().split("run.sh")[1][2:].split("$RUN_COMMAND")[0]
                break
            elif len(outs) == 0:
                solution.points += test.points
            else:
                break
        except subprocess.TimeoutExpired:
            process.kill()

#
# def limit_virtual_memory(max_memory=None):
#     max_virtual_memory = max_memory
#     if max_memory is not None:
