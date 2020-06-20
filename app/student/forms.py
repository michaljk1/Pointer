from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, SelectField, StringField, FloatField
from wtforms.validators import Optional

from app.models import solutionStatus


class UploadForm(FlaskForm):
    file = FileField('Wybierz plik')
    submit_button = SubmitField('Zapisz')


class SolutionStudentSearchForm(FlaskForm):
    course = SelectField('Kurs', choices=[['All', 'Wszystkie kursy']])
    status = SelectField('Status', choices=[[solutionStatus['ALL'], solutionStatus['ALL']],
                                            [solutionStatus['REFUSED'], solutionStatus['REFUSED']],
                                            [solutionStatus['ACTIVE'], solutionStatus['ACTIVE']]])
    lesson = StringField('Lekcja')
    exercise = StringField('Ćwiczenie')
    points_from = FloatField('Punkty od', [Optional()])
    points_to = FloatField('Punkty do', [Optional()])
    submit = SubmitField('Wyszukaj')
