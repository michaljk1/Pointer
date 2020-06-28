from flask import Blueprint

bp = Blueprint('default', __name__)

from pointer.default import routes
