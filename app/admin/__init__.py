from flask import Blueprint

bp = Blueprint('admin', __name__)

from app.admin import other_routes, course_route, exercise_route, lesson_route, solution_route, export_routes
