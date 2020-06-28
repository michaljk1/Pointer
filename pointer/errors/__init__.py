from flask import Blueprint

bp = Blueprint('errors', __name__)

from pointer.errors import handlers
