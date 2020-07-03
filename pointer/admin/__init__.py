from flask import Blueprint

bp = Blueprint('admin', __name__)

from pointer.admin import routes, course_route, exercise_route, lesson_route, solution_route
