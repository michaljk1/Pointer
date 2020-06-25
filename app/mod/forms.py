from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from app.models.logininfo import LoginInfo


class RoleForm(FlaskForm):
    email = SelectField('User', choices=[])
    roles = SelectField('Role', choices=[])
    submit_button = SubmitField('Zmień rolę')


class LoginInfoForm(FlaskForm):
    email = SelectField('User', choices=[['All', 'All']])
    status = SelectField('Status', choices=[[LoginInfo.Status['ALL'], LoginInfo.Status['ALL']],
                                            [LoginInfo.Status['ERROR'], LoginInfo.Status['ERROR']],
                                            [LoginInfo.Status['SUCCESS'], LoginInfo.Status['SUCCESS']]])
    ip_address = StringField('IP')
    submit_button = SubmitField('Wyszukaj')
