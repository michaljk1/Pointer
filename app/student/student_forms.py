# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, SelectField, StringField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired

from app.models.solution import Solution


class UploadForm(FlaskForm):
    file = FileField('Wybierz plik', validators=[DataRequired()])
    submit_button = SubmitField('Wyślij rozwiązanie')


class SolutionStudentSearchForm(FlaskForm):
    course = SelectField('Kurs', choices=[['All', 'Wszystkie kursy']])
    status = SelectField('Status', choices=[[Solution.Status['ALL'], Solution.Status['ALL']],
                                            [Solution.Status['APPROVED'], Solution.Status['APPROVED']],
                                            [Solution.Status['REFUSED'], Solution.Status['REFUSED']],
                                            [Solution.Status['NOT_ACTIVE'], Solution.Status['NOT_ACTIVE']],
                                            [Solution.Status['SEND'], Solution.Status['SEND']],
                                            [Solution.Status['COMPILE_ERROR'], Solution.Status['COMPILE_ERROR']],
                                            [Solution.Status['TEST_ERROR'], Solution.Status['TEST_ERROR']],
                                            [Solution.Status['TIMEOUT_ERROR'], Solution.Status['TIMEOUT_ERROR']]])
    lesson = StringField('Lekcja')
    exercise = StringField('Zadanie')
    submit = SubmitField('Wyszukaj')


class StudentSolutionForm(FlaskForm):
    error_msg = TextAreaField('Szczegóły błędu', render_kw={'rows': '5', 'readonly': True})
    student_status = StringField('Status', render_kw={'readonly': True})
    student_points = FloatField('Punkty', render_kw={'readonly': True})
    file_path = StringField('Plik', render_kw={'readonly': True})
    attempt = IntegerField('Próba', render_kw={'readonly': True})
    comment = TextAreaField('Komentarz', render_kw={'rows': '5', 'readonly': True})
