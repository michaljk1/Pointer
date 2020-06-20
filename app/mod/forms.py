from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField

from app.models import loginStatus


class RoleForm(FlaskForm):
    email = SelectField('User', choices=[])
    roles = SelectField('Role', choices=[])
    submit_button = SubmitField('Zmień rolę')


class LoginInfoForm(FlaskForm):
    email = SelectField('User', choices=[])
    status = SelectField('Status', choices=[[loginStatus['ALL'], loginStatus['ALL']],
                                            [loginStatus['ERROR'], loginStatus['ERROR']],
                                            [loginStatus['SUCCESS'], loginStatus['SUCCESS']]])
    submit_button = SubmitField('Wyszukaj')
