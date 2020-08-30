# -*- coding: utf-8 -*-
from flask import abort

from app.models.exercise import Exercise
from app.models.lesson import Lesson
from app.models.solution import Solution
from app.models.test import Test
from app.models.usercourse import Course, User, Member


def validate_role(user: User, required_role: str):
    if user.role != required_role:
        abort(404)


def validate_exists(my_object):
    if my_object is None:
        abort(404)


def validate_course(member: Member, required_role: str, course: Course):
    validate_exists(course)
    validate_role(member, required_role)
    if course not in member.courses:
        abort(404)


def validate_lesson(member: Member, required_role: str, lesson: Lesson):
    validate_exists(lesson)
    validate_course(member, required_role, lesson.get_course())


def validate_test(member: Member, required_role: str, test: Test):
    validate_exists(test)
    validate_course(member, required_role, test.get_course())


def validate_exercise_teacher(member: Member, required_role: str, exercise: Exercise):
    validate_exists(exercise)
    validate_course(member, required_role, exercise.get_course())


def validate_exercise_student(member: Member, required_role: str, exercise: Exercise):
    validate_exists(exercise)
    validate_course(member, required_role, exercise.get_course())
    if not exercise.is_published:
        abort(404)


def validate_solution_student(member: Member, required_role: str, solution: Solution):
    validate_exists(solution)
    validate_course(member, required_role, solution.get_course())
    if solution.author.email != member.email:
        abort(404)


def validate_solution_teacher(member: Member, required_role: str, solution: Solution):
    validate_exists(solution)
    validate_course(member, required_role, solution.get_course())

