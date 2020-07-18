#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models.domain import Domain
from app.models.usercourse import User


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
    password = PasswordField('Hasło', validators=[DataRequired()])
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
    login = StringField('Login', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Imię', validators=[DataRequired(), Length(min=1, max=20)])
    index = StringField('Nr indeksu', validators=[DataRequired(), Length(min=1, max=30)])
    surname = StringField('Nazwisko', validators=[DataRequired(), Length(min=1, max=40)])
    submit = SubmitField('Zarejestruj się')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Podany adres email jest zajęty.')
        if '@' in email.data:
            email_domain = email.data.split('@')[1]
            domains = Domain.query.all()
            is_proper = False
            for domain in domains:
                if email_domain == domain.name:
                    is_proper = True
            if not is_proper:
                raise ValidationError('Rejestracja dla danej domeny nie jest możliwa.')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Podany login jest zajęty.')

    def validate_index(self, index):
        user = User.query.filter_by(index=index.data).first()
        if user is not None:
            raise ValidationError('Podany indeks jest zajęty.')
