# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField

from app.models.logininfo import LoginInfo


class RoleStudentForm(FlaskForm):
    email = SelectField('User', choices=[])
    submit_button = SubmitField('Nadaj uprawnienia studenta')


class RoleAdminForm(FlaskForm):
    email = SelectField('User', choices=[])
    submit_button = SubmitField('Nadaj uprawnienia nauczyciela')


class LoginInfoForm(FlaskForm):
    email = SelectField('Email', choices=[['ALL', 'Dowolny']])
    status = SelectField('Status', choices=[[LoginInfo.Status['ALL'], LoginInfo.Status['ALL']],
                                            [LoginInfo.Status['ERROR'], LoginInfo.Status['ERROR']],
                                            [LoginInfo.Status['SUCCESS'], LoginInfo.Status['SUCCESS']]])
    ip_address = StringField('IP')
    submit_button = SubmitField('Wyszukaj')
