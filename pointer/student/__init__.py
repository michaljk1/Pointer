from flask import Blueprint

bp = Blueprint('student', __name__)

from pointer.student import student_routes
