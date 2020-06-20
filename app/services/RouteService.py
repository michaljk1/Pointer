from flask import abort, redirect, url_for


def validate_role(user, role):
    if user.role != role:
        abort(404)


def validate_role_course(user, role, course):
    if user.role != role or course not in user.courses:
        abort(404)


def validate_role_solution(user, role, solution):
    if user.role != role or solution.author.email != user.email:
        abort(404)


def validate_exists(my_object):
    if my_object is None:
        abort(404)


def redirect_for_index_by_role(role):
    if role == role['STUDENT']:
        redirect(url_for('student.index'))
    elif role == role['ADMIN']:
        return redirect(url_for('admin.index'))
    elif role == role['MODERATOR']:
        return redirect(url_for('mod.index'))
