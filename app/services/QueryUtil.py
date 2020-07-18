#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
from sqlalchemy import desc
from app import db
from app.mod.mod_forms import LoginInfoForm
from app.models.logininfo import LoginInfo
from app.models.solution import Solution
from app.models.usercourse import User, Course
from app.models.lesson import Lesson
from app.models.exercise import Exercise


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


def exercise_admin_query(form, courses=None):
    query = exercise_query(form, courses)

    if form.status.data != Solution.Status['ALL'] and form.status.data != 'None':
        query = query.filter(Solution.status == form.status.data)

    if form.surname.data is not None and len(form.surname.data) > 0:
        query = query.filter(User.surname == form.surname.data)

    if form.name.data is not None and len(form.name.data) > 0:
        query = query.filter(User.name == form.name.data)

    if form.index.data is not None and len(form.index.data) > 0:
        query = query.filter(User.index == form.index.data)

    if form.email.data is not None and len(form.email.data) > 0:
        query = query.filter(User.email == form.email.data)

    if form.ip_address.data is not None and len(form.ip_address.data) > 0:
        query = query.filter(Solution.ip_address == form.ip_address.data)

    if form.points_from.data is not None:
        query = query.filter(Solution.points >= form.points_from.data)

    if form.points_to.data is not None:
        query = query.filter(Solution.points <= form.points_to.data)

    return query.order_by(desc(Solution.send_date))


def exercise_student_query(form, student_id, courses):
    return exercise_query(form, courses).filter(User.id == student_id)


def exercise_query(form, courses=None):
    query = db.session.query(Solution).select_from(Solution, User, Course, Lesson, Exercise). \
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
        query = query.filter(Lesson.name == form.lesson.data)

    if not len(form.exercise.data) == 0:
        query = query.filter(Exercise.name == form.exercise.data)

    return query


# admin can see only his courses members login infos, ids = list ids of course members
def login_query(form: LoginInfoForm, user_role: str, members_ids=None):
    query = db.session.query(LoginInfo).select_from(LoginInfo).join(User, User.id == LoginInfo.user_id)

    if form.status.data != LoginInfo.Status['ALL']:
        query = query.filter(LoginInfo.status == form.status.data)

    if form.ip_address.data != '':
        query = query.filter(LoginInfo.ip_address == form.ip_address.data)

    if form.email.data != 'ALL':
        query = query.filter(User.email == form.email.data)
    elif user_role == User.Roles['MODERATOR']:
        query = query.filter(User.role == User.Roles['ADMIN'])
    elif user_role == User.Roles['ADMIN']:
        if members_ids is None or len(members_ids) == 0:
            query = query.filter(1 == 0)
        else:
            query = query.filter(User.id.in_(members_ids))
    return query
