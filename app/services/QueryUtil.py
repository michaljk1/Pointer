# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy import desc, func

from app import db
from app.admin.admin_forms import LoginInfoForm
from app.models.exercise import Exercise
from app.models.lesson import Lesson
from app.models.logininfo import LoginInfo
from app.models.solution import Solution
from app.models.usercourse import User, Course, Student


# student shouldn't be able to view approved or refused status if exercise is not finished
def get_filtered_by_status(solutions: List[Solution], status: str) -> List[Solution]:
    qualified_solutions = []
    finish_statuses = [Solution.Status['APPROVED'], Solution.Status['NOT_ACTIVE'], Solution.Status['REFUSED']]
    if status == Solution.Status['ALL']:
        return solutions
    else:
        if status not in finish_statuses:
            for solution in solutions:
                if solution.status == status:
                    qualified_solutions.append(solution)
        else:
            for solution in solutions:
                if solution.exercise.is_finished():
                    if solution.status == status:
                        qualified_solutions.append(solution)
                else:
                    if status == Solution.Status['NOT_ACTIVE'] and solution.status in finish_statuses:
                        qualified_solutions.append(solution)
    return qualified_solutions


def exercise_teacher_query(form, courses=None):
    query = exercise_query(form, courses)

    if form.is_published.data:
        query = query.filter(Exercise.is_published == True)

    if form.status.data != Solution.Status['ALL'] and form.status.data != 'None':
        query = query.filter(Solution.status == form.status.data)

    if not is_string_empty(form.surname.data):
        query = query.filter(func.lower(Student.surname) == func.lower(form.surname.data))

    if not is_string_empty(form.name.data):
        query = query.filter(func.lower(Student.name) == func.lower(form.name.data))

    if not is_string_empty(form.university_id.data):
        query = query.filter(Student.university_id == form.university_id.data)

    if not is_string_empty(form.email.data):
        query = query.filter(func.lower(Student.email) == func.lower(form.email.data))

    if not is_string_empty(form.ip_address.data):
        query = query.filter(Solution.ip_address == form.ip_address.data)

    if form.points_from.data is not None:
        query = query.filter(Solution.points >= form.points_from.data)

    if form.points_to.data is not None:
        query = query.filter(Solution.points <= form.points_to.data)

    return query.order_by(desc(Solution.send_date))


def exercise_student_query(form, student_id, courses):
    query = exercise_query(form, courses).filter(User.id == student_id)
    query = query.filter(Exercise.is_published == True)
    return query


def exercise_query(form, courses=None):
    query = db.session.query(Solution).select_from(Solution, Student, Course, Lesson, Exercise). \
        join(User, User.id == Solution.user_id). \
        join(Exercise, Solution.exercise_id == Exercise.id). \
        join(Lesson, Lesson.id == Exercise.lesson_id). \
        join(Course, Course.id == Lesson.course_id)

    query = query.filter(User.role == User.Roles['STUDENT'])

    if form.course.data != 'All':
        query = query.filter(Course.name == form.course.data)
    else:
        if courses is None:
            query = query.filter(1 == 0)
        else:
            query = query.filter(Course.name.in_(courses))

    if not len(form.lesson.data) == 0:
        query = query.filter(func.lower(Lesson.name) == func.lower(form.lesson.data))

    if not len(form.exercise.data) == 0:
        query = query.filter(func.lower(Exercise.name) == func.lower(form.exercise.data))

    return query


# teacher can see only his own and his courses members login infos
def login_query(form: LoginInfoForm, user_role: str, member_emails=None):
    query = db.session.query(LoginInfo).select_from(LoginInfo).join(User, User.id == LoginInfo.user_id)

    if form.status.data != LoginInfo.Status['ALL']:
        query = query.filter(LoginInfo.status == form.status.data)

    if not is_string_empty(form.ip_address.data):
        query = query.filter(LoginInfo.ip_address == form.ip_address.data)

    if form.email.data != 'ALL':
        query = query.filter(User.email == form.email.data)
    elif user_role == User.Roles['TEACHER']:
        if member_emails is None or len(member_emails) == 0:
            query = query.filter(1 == 0)
        else:
            query = query.filter(User.email.in_(member_emails))
    return query.order_by(desc(LoginInfo.login_date))


def is_string_empty(my_string: str) -> bool:
    return my_string is None or len(my_string) == 0
