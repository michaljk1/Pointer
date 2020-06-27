from flask import abort, redirect, url_for
from app.models.usercourse import role


def validate_role(user, user_role):
    if user.role != user_role:
        abort(404)


def validate_role_course_name(user, user_role, course):
    if user.role != user_role or user.get_course_by_name(course) is None:
        abort(404)


def validate_role_course(user, user_role, course):
    if user.role != user_role or course is None or course not in user.courses:
        abort(404)


def validate_role_solution(user, user_role, solution):
    if user.role != user_role or solution.author.email != user.email:
        abort(404)


def validate_exists(my_object):
    if my_object is None:
        abort(404)


def redirect_for_index_by_role(user_role):
    if user_role == role['STUDENT']:
        return redirect(url_for('student.index'))
    elif user_role == role['ADMIN']:
        return redirect(url_for('admin.index'))
    elif user_role == role['MODERATOR']:
        return redirect(url_for('mod.index'))
