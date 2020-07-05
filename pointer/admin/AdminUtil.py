from typing import List

from pointer import db
from pointer.models.solution import Solution
from pointer.models.usercourse import Course, role


def get_student_ids_emails(courses: List[Course]):
    user_ids, emails = [], []
    for course in courses:
        for member in course.members:
            if member.role == role['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                emails.append((member.email, member.email))
    return user_ids, emails
