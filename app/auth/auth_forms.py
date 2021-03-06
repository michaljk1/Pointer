# -*- coding: utf-8 -*-
from flask import current_app
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app.models.usercourse import User, Member


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Wprowadź dane')])
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
    password = PasswordField('Hasło', validators=[DataRequired(), Length(max=40)])
    password2 = PasswordField(
        'Wprowadź ponownie', validators=[DataRequired(), EqualTo('password', message='Wprowadzone hasła różnią się')])

    def validate_password(self, password):
        password_str = password.data
        if not (any(x.isupper() for x in password_str) and any(x.islower() for x in password_str)
                and any(x.isdigit() for x in password_str) and len(password_str) >= 8):
            raise ValidationError('Hasło musi zawierać minimum 8 znaków, cyfrę, jedną małą oraz dużą literę')


class ChangePasswordForm(PasswordForm):
    actual_password = PasswordField('Aktualne hasło')
    submit = SubmitField('Zmień hasło')


class ResetPasswordForm(PasswordForm):
    submit = SubmitField('Zmień hasło')


class RegistrationForm(PasswordForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=70)])
    name = StringField('Imię', validators=[DataRequired(), Length(min=1, max=20)])
    university_id = StringField('Identyfikator', validators=[DataRequired(), Length(min=1, max=30)])
    surname = StringField('Nazwisko', validators=[DataRequired(), Length(min=1, max=40)])
    submit = SubmitField('Zarejestruj się')

    def validate_name(self, name):
        if not name.data.isalpha():
            raise ValidationError('Wprowadzono niepoprawne znaki.')

    def validate_surname(self, surname):
        if not surname.data.isalpha():
            raise ValidationError('Wprowadzono niepoprawne znaki.')

    def validate_email(self, email):
        user = User.query.filter(func.lower(User.email) == func.lower(email.data)).first()
        if user is not None:
            raise ValidationError('Podany adres email jest zajęty.')
        if '@' in email.data:
            email_domain = email.data.split('@')[1]
            is_proper = False
            for domain in current_app.config['ALLOWED_DOMAINS']:
                if email_domain == domain:
                    is_proper = True
                    break
            if not is_proper:
                raise ValidationError('Rejestracja dla danej domeny nie jest możliwa.')

    def validate_university_id(self, university_id):
        member = Member.query.filter_by(university_id=university_id.data).first()
        if member is not None:
            raise ValidationError('Podany indeks jest zajęty.')
        if not university_id.data.isdecimal():
            raise ValidationError('Wprowadzono niepoprawne znaki')
