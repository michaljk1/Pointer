
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List
from app.services.DateUtil import get_current_date, get_offset_aware
from app.models.solution import Solution


def can_send_solution(sorted_solutions: List[Solution]) -> bool:
    solutions_amount = len(sorted_solutions)
    if solutions_amount == 0:
        return True
    else:
        last_solution = sorted_solutions[0]
        second_difference = (get_current_date() - get_offset_aware(last_solution.send_date)).seconds
        return second_difference > last_solution.exercise.interval
