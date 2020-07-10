from typing import List

from pointer.models.statistics import Statistics
from pointer.models.usercourse import Course, role, User


def get_students_ids_emails(courses: List[Course]):
    user_ids, emails = [], []
    for course in courses:
        for member in course.members:
            if member.role == role['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                emails.append(member.email)
    return user_ids, emails


def get_statistics(users: List[User], courses: List[Course]):
    statistics_list = []
    for course in courses:
        for user in users:
            statistics_list.append(Statistics(course=course, user=user, is_admin=True))
    return statistics_list
