from flask import Blueprint

bp = Blueprint('admin', __name__)

from pointer.admin import routes
