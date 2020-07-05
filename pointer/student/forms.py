from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, SelectField, StringField, FloatField
from wtforms.validators import Optional, DataRequired

from pointer.models.solution import Solution


class UploadForm(FlaskForm):
    file = FileField('Wybierz plik', validators=[DataRequired()])
    submit_button = SubmitField('Zapisz')


class SolutionStudentSearchForm(FlaskForm):
    course = SelectField('Kurs', choices=[['All', 'Wszystkie kursy']])
    status = SelectField('Status', choices=[[Solution.Status['ALL'], Solution.Status['ALL']],
                                            [Solution.Status['APPROVED'], Solution.Status['APPROVED']],
                                            [Solution.Status['REFUSED'], Solution.Status['REFUSED']],
                                            [Solution.Status['NOT_ACTIVE'], Solution.Status['NOT_ACTIVE']],
                                            [Solution.Status['SEND'], Solution.Status['SEND']],
                                            [Solution.Status['COMPILE_ERROR'], Solution.Status['COMPILE_ERROR']],
                                            [Solution.Status['TEST_ERROR'], Solution.Status['TEST_ERROR']],
                                            [Solution.Status['ERROR'], Solution.Status['ERROR']]])
    lesson = StringField('Lekcja')
    exercise = StringField('Ćwiczenie')
    submit = SubmitField('Wyszukaj')
