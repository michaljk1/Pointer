from flask import url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app.default import bp
from app.models.usercourse import role


@bp.route('/')
@bp.route('/index')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    elif current_user.role == role['ADMIN']:
        return redirect(url_for('admin.view_courses'))
    elif current_user.role == role['STUDENT']:
        return redirect(url_for('student.view_courses'))
    elif current_user.role == role['MODERATOR']:
        return redirect(url_for('mod.index'))
    else:
        return redirect(url_for('auth.login'))
