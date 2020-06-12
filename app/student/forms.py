from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, SelectField, StringField, BooleanField, FloatField
from wtforms.validators import Optional


class UploadForm(FlaskForm):
    file = FileField('Select File')
    submit_button = SubmitField('Submit Form')


class SolutionStudentSearchForm(FlaskForm):
    course = SelectField('Course', choices=[])
    lesson = StringField('Lesson')
    exercise_name = StringField('Ćwiczenie')
    all = BooleanField('Wszystkie')
    admin_refused = BooleanField('Odrzucone')
    is_active = BooleanField('Aktywne')
    points_from = FloatField('Punkty od', [Optional()])
    points_to = FloatField('Punkty do', [Optional()])
    submit = SubmitField('Wyszukaj')
