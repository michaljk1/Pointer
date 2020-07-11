from flask import Blueprint

bp = Blueprint('auth', __name__)

from pointer.auth import auth_routes
