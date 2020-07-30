# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectField


class EmailForm(FlaskForm):
    email = SelectField('Email', choices=[])
