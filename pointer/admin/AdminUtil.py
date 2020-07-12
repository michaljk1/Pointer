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


def get_statistics(user: User, course: Course, admin_courses: List[Course]):
    statistics_list, statistics_info = [], []
    if course is None:
        if user is None:
            for course in admin_courses:
                for member in course.get_students():
                    statistics_list.append(Statistics(course=course, user=member, is_admin=True))
        else:
            statistics_list = prepare_statistics([user], user.courses)
    else:
        if user is None:
            statistics_list = prepare_statistics(course.get_students(), [course])
        else:
            if course in user.courses:
                statistics_list = prepare_statistics([user], [course])
    for statistics in statistics_list:
        statistics_info.append([statistics.course_id, statistics.user_id])
    return statistics_list, statistics_info


def prepare_statistics(users: List[User], courses: List[Course]):
    statistics_list = []
    for course in courses:
        for user in users:
            statistics_list.append(Statistics(course=course, user=user, is_admin=True))
    return statistics_list


def get_statistics_by_ids(infos):
    statistics = []
    for info in infos:
        course_id, user_id = info.strip('()').strip('[]').split(',')
        course = Course.query.filter_by(id=course_id).first()
        user = User.query.filter_by(id=user_id).first()
        statistics.append(Statistics(course, user, True))
    return statistics
