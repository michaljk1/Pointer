from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField

from app.models import LoginInfo


class RoleForm(FlaskForm):
    email = SelectField('User', choices=[])
    roles = SelectField('Role', choices=[])
    submit_button = SubmitField('Zmień rolę')


class LoginInfoForm(FlaskForm):
    email = SelectField('User', choices=[['All', 'All']])
    status = SelectField('Status', choices=[[LoginInfo.loginStatus['ALL'], LoginInfo.loginStatus['ALL']],
                                            [LoginInfo.loginStatus['ERROR'], LoginInfo.loginStatus['ERROR']],
                                            [LoginInfo.loginStatus['SUCCESS'], LoginInfo.loginStatus['SUCCESS']]])
    submit_button = SubmitField('Wyszukaj')
