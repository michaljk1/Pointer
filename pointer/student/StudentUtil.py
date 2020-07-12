import os
import shutil
from typing import List
from pointer.DateUtil import get_current_date, get_offset_aware
from pointer.models.solution import Solution


def can_send_solution(sorted_solutions: List[Solution]):
    solutions_amount = len(sorted_solutions)
    if solutions_amount == 0:
        return True
    else:
        last_solution = sorted_solutions[0]
        second_difference = (get_current_date() - get_offset_aware(last_solution.send_date)).seconds
        return second_difference > last_solution.exercise.interval


def unpack_file(filename, solution_directory):
    if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
            '.tar'):
        shutil.unpack_archive(os.path.join(solution_directory, filename), solution_directory)