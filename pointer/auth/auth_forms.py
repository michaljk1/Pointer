from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from pointer.models.usercourse import User


class LoginForm(FlaskForm):
    email = StringField('Email/Login', validators=[DataRequired(message='Wprowadź dane')])
    password = PasswordField('Hasło', validators=[DataRequired(message='Wprowadź dane')])
    remember_me = BooleanField('Zapisz')
    submit = SubmitField('Zaloguj się')


class ConfirmEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Wyślij link')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Podany adres email nie istnieje')


class PasswordForm(FlaskForm):
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=8, message='Hasło musi zawierać minimum 8 znaków')])
    password2 = PasswordField(
        'Wprowadź ponownie', validators=[DataRequired(), EqualTo('password', message='Wprowadzone hasła różnią się')])


class ChangePasswordForm(PasswordForm):
    actual_password = PasswordField('Aktualne hasło')
    submit = SubmitField('Zmień hasło')


class ResetPasswordForm(PasswordForm):
    submit = SubmitField('Zmień hasło')


class RegistrationForm(PasswordForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    login = StringField('Login', validators=[DataRequired()])
    name = StringField('Imię', validators=[DataRequired()])
    index = StringField('Nr indeksu', validators=[DataRequired()])
    surname = StringField('Nazwisko', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj się')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Podany adres email jest zajęty.')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Podany login jest zajęty.')
