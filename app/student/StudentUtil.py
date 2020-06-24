from datetime import datetime
from typing import List

from app.default.DefaultUtil import get_current_date
from app.models import Solution


def get_finished_exercises(solutions: List[Solution]):
    exercises, finished_exercises = [], []
    current_datetime = get_current_date()
    for solution in solutions:
        if solution.exercise not in exercises:
            exercises.append(solution.exercise)
    for exercise in exercises:
        end_date = exercise.end_date
        end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_date.hour,
                                minute=end_date.minute, tzinfo=current_datetime.tzinfo)
        if current_datetime > end_datetime:
            finished_exercises.append(exercise)
    return finished_exercises
