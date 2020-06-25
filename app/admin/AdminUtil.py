from typing import List

from app import db
from app.mod.forms import LoginInfoForm
from app.models.solution import Solution
from app.models.usercourse import Course, role


def get_student_ids_emails(courses: List[Course]):
    user_ids, emails = [], []
    for course in courses:
        for member in course.members:
            if member.role == role['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                emails.append((member.email, member.email))
    return user_ids, emails


def modify_solution(solution: Solution, refused: bool, points: float):
    if refused:
        solution.status = Solution.Status['REFUSED']
    else:
        solution.status = Solution.Status['SEND']
    solution.points = points
    db.session.commit()

