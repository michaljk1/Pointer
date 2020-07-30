from flask import Blueprint

bp = Blueprint('mod', __name__)

from app.admin import admin_routes
