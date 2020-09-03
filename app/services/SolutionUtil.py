# -*- coding: utf-8 -*-
import os
import resource
import subprocess
from os import listdir
from os.path import isfile, join, dirname, realpath
import psutil

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import db
from app.models.exercise import Exercise
from app.models.solution import Solution
from app.models.usercourse import Member
from app.services.DateUtil import get_current_date
from app.services.FileUtil import unpack_file, create_directory

RUN_SCRIPT_NAME = 'run.sh'
COMPILE_SCRIPT_NAME = 'compile.sh'
COMPILE_ERROR_FILENAME = 'compile_error.txt'
ERROR_TEST_FILENAME = 'error_test_run.txt'
OUTPUT_FILE_SUFFIX = '_output.txt'
SUCCESS_RETURN_CODE = 0
COMPILE_SCRIPT_PATH = join(dirname(realpath(__file__)), COMPILE_SCRIPT_NAME)
RUN_SCRIPT_PATH = join(dirname(realpath(__file__)), RUN_SCRIPT_NAME)


def add_solution(exercise: Exercise, member: Member, file: FileStorage, ip_address: str, attempt_nr: int,
                 os_info: str):
    filename = secure_filename(file.filename)
    solution = Solution(filename=filename, ip_address=ip_address, send_date=get_current_date(),
                        os_info=os_info, attempt=attempt_nr)
    exercise.solutions.append(solution)
    member.solutions.append(solution)
    solution_directory = solution.get_directory()
    create_directory(solution_directory)
    file.save(join(solution_directory, solution.filename))
    unpack_file(solution.filename, solution_directory)
    db.session.commit()
    solution.enqueue_execution()


def clear_directory(solution: Solution):
    solution_dir = solution.get_directory()
    files = [f for f in listdir(solution_dir) if isfile(join(solution_dir, f))]
    for file in files:
        if file != solution.filename:
            if not file.endswith(OUTPUT_FILE_SUFFIX) or \
                    (file.endswith(OUTPUT_FILE_SUFFIX) and solution.output_file is None):
                os.remove(join(solution_dir, file))


def execute_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    solution.init_pointing()
    if prepare_compilation(solution):
        grade(solution)
    if solution.status == Solution.Status['SEND']:
        solution.status = Solution.Status['NOT_ACTIVE']
    clear_directory(solution)


def prepare_compilation(solution) -> bool:
    compile_command = solution.exercise.compile_command
    if len(compile_command.split()) > 0:
        return execute_compilation(solution, compile_command)
    else:
        return True


def execute_compilation(solution: Solution, compile_command: str) -> bool:
    error_file = open(join(solution.get_directory(), COMPILE_ERROR_FILENAME), 'w+')
    bash_command = [COMPILE_SCRIPT_PATH, solution.get_directory(), compile_command]
    subprocess.Popen(bash_command, stderr=error_file).wait()
    if error_occurred(error_file):
        handle_compile_error(solution, error_file)
        return False
    return True


def grade(solution: Solution):
    exercise = solution.exercise
    run_command = exercise.run_command
    output_file_name = exercise.program_name + OUTPUT_FILE_SUFFIX
    for test in exercise.get_sorted_tests():
        error_file = open(join(solution.get_directory(), ERROR_TEST_FILENAME), 'w+')
        command = [RUN_SCRIPT_PATH, solution.get_directory(), test.get_input_path(),
                   test.get_output_path(), run_command, output_file_name]
        process = subprocess.Popen(command, stderr=error_file, preexec_fn=limit_memory())
        try:
            process.communicate(timeout=test.timeout)
            if error_occurred(error_file):
                handle_test_error(solution, error_file)
                break
            else:
                if process.returncode == SUCCESS_RETURN_CODE:
                    solution.test_passed(test.points)
                else:
                    solution.output_file = output_file_name
                    break
        except subprocess.TimeoutExpired:
            error_file.close()
            solution.timeout_occurred()
            break
        finally:
            kill_processes(process.pid)


def kill_processes(parent_pid):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    parent.kill()


def error_occurred(error_file) -> bool:
    error_file.close()
    return os.path.getsize(error_file.name) > 0


def handle_compile_error(solution: Solution, error_file):
    solution.status = Solution.Status['COMPILE_ERROR']
    with open(error_file.name) as f:
        solution.error_msg = clear_error_msg(f.read(), COMPILE_SCRIPT_NAME)


def handle_test_error(solution: Solution, error_file):
    solution.status = Solution.Status['TEST_ERROR']
    with open(error_file.name) as f:
        solution.error_msg = clear_error_msg(f.read(), RUN_SCRIPT_NAME)


# user should not see directory in error message
def clear_error_msg(error: str, file_name) -> str:
    if file_name in error:
        error = error.split(file_name)[1][2:].split("$RUN_COMMAND")[0]
    return error


def limit_memory():
    memory_mb = current_app.config['MAX_MEMORY_MB'] * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_mb, memory_mb))
