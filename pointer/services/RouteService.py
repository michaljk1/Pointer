from flask import abort, redirect, url_for
from pointer.models.exercise import Exercise
from pointer.models.lesson import Lesson
from pointer.models.solution import Solution
from pointer.models.test import Test
from pointer.models.usercourse import role, Course, User


def validate_role(user: User, required_role: str):
    if user.role != required_role:
        abort(404)


def validate_exists(my_object):
    if my_object is None:
        abort(404)


def validate_role_course(user: User, required_role: str, course: Course):
    validate_exists(course)
    validate_role(user, required_role)
    if course is None or course not in user.courses:
        abort(404)


def validate_role_solution(user: User, required_role: str, solution: Solution):
    validate_exists(solution)
    validate_role_course(user, required_role, solution.get_course())
    if solution.author.email != user.email:
        abort(404)


def validate_lesson(user: User, required_role: str, lesson: Lesson):
    validate_exists(lesson)
    validate_role_course(user, required_role, lesson.get_course())


def validate_test(user: User, required_role: str, test: Test):
    validate_exists(test)
    validate_role_course(user, required_role, test.get_course())


def validate_admin_exercise(user: User, required_role: str, exercise: Exercise):
    validate_exists(exercise)
    validate_role_course(user, required_role, exercise.get_course())


def validate_student_exercise(user: User, required_role: str, exercise: Exercise):
    validate_exists(exercise)
    validate_role_course(user, required_role, exercise.get_course())
    if exercise is None or not exercise.is_published:
        abort(404)


def redirect_for_index_by_role(user_role: str):
    if user_role == role['STUDENT']:
        return redirect(url_for('student.index'))
    elif user_role == role['ADMIN']:
        return redirect(url_for('admin.index'))
    elif user_role == role['MODERATOR']:
        return redirect(url_for('mod.index'))
