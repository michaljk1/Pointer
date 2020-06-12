from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class RoleForm(FlaskForm):
    email = SelectField('User', choices=[])
    roles = SelectField('Role', choices=[])
    submit_button = SubmitField('Przypisz użytkownika')
