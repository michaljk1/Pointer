from flask import Blueprint

bp = Blueprint('mod', __name__)

from pointer.mod import routes
