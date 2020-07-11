from flask import Blueprint

bp = Blueprint('mod', __name__)

from pointer.mod import mod_routes
