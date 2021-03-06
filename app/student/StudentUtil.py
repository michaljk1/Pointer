# -*- coding: utf-8 -*-
from typing import List

from app.models.exercise import Exercise
from app.models.solution import Solution
from app.services.DateUtil import get_current_date, get_offset_aware


def can_send_solution(exercise: Exercise, sorted_solutions: List[Solution]) -> bool:
    solutions_amount = len(sorted_solutions)
    if exercise.is_finished() or solutions_amount >= exercise.max_attempts:
        return False
    if solutions_amount == 0:
        return True
    else:
        last_solution = sorted_solutions[0]
        second_difference = (get_current_date() - get_offset_aware(last_solution.send_date)).seconds
        return second_difference > last_solution.exercise.interval
