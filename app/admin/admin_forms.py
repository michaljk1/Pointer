# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField

from app.default.default_forms import EmailForm
from app.models.logininfo import LoginInfo


class RoleStudentForm(EmailForm):
    submit_button = SubmitField('Odbierz uprawnienia nauczyciela')


class RoleTeacherForm(EmailForm):
    submit_button = SubmitField('Nadaj uprawnienia nauczyciela')


class LoginInfoForm(FlaskForm):
    email = SelectField('Email', choices=[['ALL', 'Dowolny']])
    status = SelectField('Status', choices=[[LoginInfo.Status['ALL'], LoginInfo.Status['ALL']],
                                            [LoginInfo.Status['ERROR'], LoginInfo.Status['ERROR']],
                                            [LoginInfo.Status['SUCCESS'], LoginInfo.Status['SUCCESS']]])
    ip_address = StringField('IP')
    submit_button = SubmitField('Wyszukaj')
