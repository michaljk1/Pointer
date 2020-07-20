# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app import db
from app.services.DateUtil import get_current_date
from app.models.exercise import Exercise
from app.models.solution import Solution
from app.models.usercourse import User
import resource

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
    if not os.path.exists(solution_directory):
        os.makedirs(solution_directory)
    file.save(os.path.join(solution_directory, solution.file_path))
    unpack_file(solution.file_path, solution_directory)
    db.session.commit()
    solution.launch_execute('point_solution', 'Pointing solution')


def unpack_file(filename, solution_directory):
    if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
            '.tar'):
        shutil.unpack_archive(os.path.join(solution_directory, filename), solution_directory)


def execute_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    solution.points = 0
    if prepare_compilation(solution):
        grade(solution)
    if solution.status == Solution.Status['SEND']:
        solution.status = Solution.Status['NOT_ACTIVE']
    if solution.status not in [Solution.Status['COMPILE_ERROR'], Solution.Status['TEST_ERROR'],
                               Solution.Status['ERROR']]:
        solution.error_msg = None
    # reprocessing task case
    if solution.status == Solution.Status['APPROVED']:
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
            solution.error_msg = f.read()
        solution.status = Solution.Status['COMPILE_ERROR']
        return False
    else:
        os.remove(error_file.name)
        return True


def grade(solution: Solution):
    exercise = solution.exercise
    program_name, run_command = exercise.program_name, exercise.run_command
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), RUN_SCRIPT_NAME)
    for test in exercise.tests.all():
        name = 'error_test_run' + str(test.id) + '.txt'
        error_file = open(os.path.join(solution.get_directory(), name), 'w+')
        output_file_name = program_name + "_output_student.txt"
        command = [script_path, solution.get_directory(), program_name, test.get_input_path(),
                   test.get_output_path(), run_command, output_file_name]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=error_file, preexec_fn=limit_memory())
        try:
            outs = process.communicate(timeout=exercise.timeout)[0]
            error_file.close()
            if os.path.getsize(error_file.name) > 0:
                solution.status = Solution.Status['TEST_ERROR']
                with open(error_file.name) as f:
                    solution.error_msg = clear_error_msg(f.read())
                break
            else:
                os.remove(error_file.name)
                if len(outs) == 0:
                    os.remove(os.path.join(solution.get_directory(), output_file_name))
                    solution.points += test.points
                else:
                    break
        except subprocess.TimeoutExpired:
            process.kill()
            solution.error_msg = 'Przekroczono limit czasu podczas testowania'
            solution.status = solution.Status['ERROR']
            break


# user should not see directory in error message
def clear_error_msg(error: str) -> str:
    if RUN_SCRIPT_NAME in error:
        error = error.split(RUN_SCRIPT_NAME)[1][2:].split("$RUN_COMMAND")[0]
    return error


def limit_memory():
    config_memory = current_app.config['MAX_MEMORY_MB']
    memory_mb = config_memory * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_mb, memory_mb))
