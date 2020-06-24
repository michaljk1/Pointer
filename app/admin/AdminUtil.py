from typing import List

from app import db
from app.mod.forms import LoginInfoForm
from app.models import Course, role, Solution


def get_filled_form_with_ids(courses: List[Course]):
    user_ids = []
    form = LoginInfoForm()
    for course in courses:
        for member in course.members:
            if member.role == role['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                form.email.choices.append((member.email, member.email))
    return user_ids, form


def modify_solution(solution: Solution, refused: bool, points: float):
    if refused:
        solution.status = Solution.Status['REFUSED']
    else:
        solution.status = Solution.Status['SEND']
    solution.points = points
    db.session.commit()