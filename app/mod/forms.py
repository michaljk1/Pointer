from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField

class RoleForm(FlaskForm):
    email = SelectField('User', choices=[])
    role = SelectField('Role', choices=[])
    submit_button = SubmitField('Przypisz użytkownika')
