#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app.default import bp
from app.default.DefaultUtil import redirect_for_index_by_role


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    redirect_for_index_by_role(current_user.role)


