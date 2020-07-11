from typing import List

from pointer.DefaultUtil import get_current_date, get_offset_aware
from pointer.models.solution import Solution


def can_send_solution(sorted_solutions: List[Solution]):
    solutions_amount = len(sorted_solutions)
    if solutions_amount == 0:
        return True
    else:
        last_solution = sorted_solutions[0]
        return (get_current_date() - get_offset_aware(
            last_solution.send_date)).seconds > last_solution.exercise.interval
