from flask import abort


class RouteService:
    @staticmethod
    def validate_role(user, role):
        if user.role != role:
            abort(404)

    @staticmethod
    def validate_role_course(user, role, course):
        if user.role != role or course not in user.courses:
            abort(404)

    @staticmethod
    def validate_role_solution(user, role, solution):
        if user.role != role or solution.author.email != user.email:
            abort(404)

    @staticmethod
    def validate_exists(my_object):
        if my_object is None:
            abort(404)
