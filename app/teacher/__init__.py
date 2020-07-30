from flask import Blueprint

bp = Blueprint('teacher', __name__)

from app.teacher import other_routes, course_route, exercise_route, lesson_route, solution_route, export_routes
