from flask import Blueprint

bp = Blueprint('mod', __name__)

from app.mod import admin_routes
