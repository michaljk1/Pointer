# -*- coding: utf-8 -*-
from flask import url_for
from werkzeug.utils import redirect

from app.models.usercourse import User


def redirect_for_index_by_role(user_role: str):
    if user_role == User.Roles['STUDENT']:
        return redirect(url_for('student.view_courses'))
    elif user_role == User.Roles['TEACHER']:
        return redirect(url_for('teacher.view_courses'))
    elif user_role == User.Roles['ADMIN']:
        return redirect(url_for('admin.index'))
    else:
        return redirect(url_for('auth.login'))