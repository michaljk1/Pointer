from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, SelectField, StringField, FloatField
from wtforms.validators import Optional, DataRequired

from app.models import Solution


class UploadForm(FlaskForm):
    file = FileField('Wybierz plik', validators=[DataRequired()])
    submit_button = SubmitField('Zapisz')


class SolutionStudentSearchForm(FlaskForm):
    course = SelectField('Kurs', choices=[['All', 'Wszystkie kursy']])
    status = SelectField('Status', choices=[[Solution.Status['ALL'], Solution.Status['ALL']],
                                            [Solution.Status['REFUSED'], Solution.Status['REFUSED']],
                                            [Solution.Status['ACTIVE'], Solution.Status['ACTIVE']]])
    lesson = StringField('Lekcja')
    exercise = StringField('Ćwiczenie')
    points_from = FloatField('Punkty od', [Optional()])
    points_to = FloatField('Punkty do', [Optional()])
    submit = SubmitField('Wyszukaj')
