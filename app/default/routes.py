#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import url_for
from werkzeug.utils import redirect
from app.default import bp


@bp.route('/')
def index():
    return redirect(url_for('auth.index'))

