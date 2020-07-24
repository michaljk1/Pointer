# -*- coding: utf-8 -*-
import os
import subprocess
import resource
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app import db
from app.services.DateUtil import get_current_date
from app.models.exercise import Exercise
from app.models.solution import Solution
from app.models.usercourse import User
from app.services.FileUtil import unpack_file, create_directory

RUN_SCRIPT_NAME = 'run.sh'
COMPILE_SCRIPT_NAME = 'compile.sh'


def add_solution(exercise: Exercise, current_user: User, file: FileStorage, ip_address: str, attempt_nr: int,
                 os_info: str):
    filename = secure_filename(file.filename)
    solution = Solution(file_path=filename, ip_address=ip_address, send_date=get_current_date(),
                        os_info=os_info, attempt=attempt_nr)
    exercise.solutions.append(solution)
    current_user.solutions.append(solution)
    solution_directory = solution.get_directory()
    create_directory(solution_directory)
    file.save(os.path.join(solution_directory, solution.file_path))
    unpack_file(solution.file_path, solution_directory)
    db.session.commit()
    solution.launch_execute('point_solution', 'Pointing solution')


def execute_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    solution.points = 0
    solution.status = Solution.Status['SEND']
    solution.output_file, solution.error_msg = None, None
    if prepare_compilation(solution):
        grade(solution)
    if solution.status == Solution.Status['SEND']:
        solution.status = Solution.Status['NOT_ACTIVE']


def prepare_compilation(solution) -> bool:
    compile_command = solution.exercise.compile_command
    if len(compile_command.split()) > 0:
        return execute_compilation(solution, compile_command)
    else:
        return True


def execute_compilation(solution: Solution, compile_command: str) -> bool:
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), COMPILE_SCRIPT_NAME)
    error_file = open(os.path.join(solution.get_directory(), 'compile_error.txt'), 'w+')
    bash_command = [script_path, solution.get_directory(), compile_command]
    process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=error_file)
    process.wait()
    error_file.close()
    if os.path.getsize(error_file.name) > 0:
        with open(error_file.name) as f:
            solution.error_msg = clear_error_msg(f.read(), COMPILE_SCRIPT_NAME)
        solution.status = Solution.Status['COMPILE_ERROR']
        return False
    else:
        os.remove(error_file.name)
        return True


def grade(solution: Solution):
    exercise = solution.exercise
    program_name, run_command = exercise.program_name, exercise.run_command
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), RUN_SCRIPT_NAME)
    sorted_tests = sorted(exercise.tests.all(), key=lambda t: t.create_date)
    for test in sorted_tests:
        name = 'error_test_run' + str(test.id) + '.txt'
        error_file = open(os.path.join(solution.get_directory(), name), 'w+')
        output_file_name = program_name + "_output.txt"
        command = [script_path, solution.get_directory(), program_name, test.get_input_path(),
                   test.get_output_path(), run_command, output_file_name]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=error_file, preexec_fn=limit_memory())
        try:
            out_process = process.communicate(timeout=exercise.timeout)[0]
            process.wait()
            error_file.close()
            if os.path.getsize(error_file.name) > 0:
                solution.status = Solution.Status['TEST_ERROR']
                with open(error_file.name) as f:
                    solution.error_msg = clear_error_msg(f.read(), RUN_SCRIPT_NAME)
                break
            else:
                os.remove(error_file.name)
                if 'PASSED' in str(out_process):
                    solution.points += test.points
                    solution.output_file = None
                else:
                    solution.output_file = output_file_name
                    break
        except subprocess.TimeoutExpired:
            process.kill()
            solution.error_msg = 'Przekroczono limit czasu podczas testowania'
            solution.status = solution.Status['ERROR']
            break


# user should not see directory in error message
def clear_error_msg(error: str, file_name) -> str:
    if file_name in error:
        error = error.split(file_name)[1][2:].split("$RUN_COMMAND")[0]
    return error


def limit_memory():
    memory_mb = current_app.config['MAX_MEMORY_MB'] * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_mb, memory_mb))
