from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, ValidationError

from pointer.models.domain import Domain
from pointer.models.logininfo import LoginInfo


class RoleStudentForm(FlaskForm):
    email = SelectField('User', choices=[])
    submit_button = SubmitField('Nadaj uprawnienia studenta')


class DomainForm(FlaskForm):
    domain = StringField('Domena')
    submit_button = SubmitField('Dodaj')

    def validate_domain(self, domain):
        domain = Domain.query.filter_by(name=domain.data).first()
        if domain is not None:
            raise ValidationError('Podana domena już istnieje')


class RoleAdminForm(FlaskForm):
    email = SelectField('User', choices=[])
    submit_button = SubmitField('Nadaj uprawnienia administratora')


class LoginInfoForm(FlaskForm):
    email = SelectField('Użytkownik', choices=[['ALL', 'Dowolny']])
    status = SelectField('Status', choices=[[LoginInfo.Status['ALL'], LoginInfo.Status['ALL']],
                                            [LoginInfo.Status['ERROR'], LoginInfo.Status['ERROR']],
                                            [LoginInfo.Status['SUCCESS'], LoginInfo.Status['SUCCESS']]])
    ip_address = StringField('IP')
    submit_button = SubmitField('Wyszukaj')
