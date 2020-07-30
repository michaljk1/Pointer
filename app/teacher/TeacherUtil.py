from typing import List

from app.models.statistics import Statistics
from app.models.usercourse import Course, Student


def get_students_ids_emails(courses: List[Course]) -> (List[int], List[str]):
    student_ids, emails = [], []
    for course in courses:
        for student in course.get_students():
            student_ids.append(student.id)
            emails.append(student.email)
    return list(set(student_ids)), list(set(emails))


def get_statistics(student: Student, course: Course, teacher_courses: List[Course]) -> (List[object], List[List[int]]):
    statistics_list, statistics_info = [], []
    if course is None:
        # statistics for all students in all teacher courses
        if student is None:
            for course in teacher_courses:
                for student in course.get_students():
                    statistics_list.append(Statistics(course=course, student=student, for_teacher=True))
        # statistics for student in intersection of user and teacher courses
        else:
            statistics_list = Statistics.prepare_statistics([student], list(set(teacher_courses).intersection(set(student.courses))))
    else:
        if student is None:
            statistics_list = Statistics.prepare_statistics(course.get_students(), [course])
        else:
            if course in student.courses:
                statistics_list = [Statistics(course=course, student=student, for_teacher=True)]
    # fill info about course and user id needed for regenerating during export
    for statistics in statistics_list:
        statistics_info.append([statistics.course_id, statistics.user_id])
    return statistics_list, statistics_info

