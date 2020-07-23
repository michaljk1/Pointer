from typing import List
from app.models.statistics import Statistics
from app.models.usercourse import Course, User


def get_students_ids_emails(courses: List[Course]) -> (List[int], List[str]):
    user_ids, emails = [], []
    for course in courses:
        for member in course.members:
            if member.role == User.Roles['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                emails.append(member.email)
    return user_ids, emails


def get_statistics(user: User, course: Course, admin_courses: List[Course]) -> (List[object], List[List[int]]):
    statistics_list, statistics_info = [], []
    if course is None:
        # statistics for all students in all admin courses
        if user is None:
            for course in admin_courses:
                for member in course.get_students():
                    statistics_list.append(Statistics(course=course, user=member, for_admin=True))
        # statistics for all students in all admin courses
        else:
            statistics_list = Statistics.prepare_statistics([user], list(set(admin_courses).intersection(set(user.courses))))
    else:
        if user is None:
            statistics_list = Statistics.prepare_statistics(course.get_students(), [course])
        else:
            if course in user.courses:
                statistics_list = [Statistics(course=course, user=user, for_admin=True)]
    # fill info about course and user id needed for regenerating during export
    for statistics in statistics_list:
        statistics_info.append([statistics.course_id, statistics.user_id])
    return statistics_list, statistics_info

