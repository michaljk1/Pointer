from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, FieldList, \
    SelectField, FormField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email


class UploadForm(FlaskForm):
    file = FileField('Select File')
    submit_button = SubmitField('Submit Form')


class CourseForm(FlaskForm):
    name = StringField('Course name')
    submit_button = SubmitField('Dodaj kurs')


class LessonForm(FlaskForm):
    name = StringField('Lesson name')
    text_content = StringField('Content')
    pdf_content = FileField('Select File')
    content_url = StringField('Url')
    submit_button = SubmitField('Dodaj lekcję')


class TemplateForm(FlaskForm):
    name = StringField('Nazwa')
    content = StringField('content')
    max_attempts = IntegerField('Liczba prób', default=3)
    max_points = FloatField('Liczba punktów')
    end_date = DateField('End date', format='%Y-%m-%d')
    compile_command = StringField('compile command')
    run_command = StringField('run_command')
    output = FileField('Output')
    input = FileField('Input')
    submit_button = SubmitField('Dodaj ćwiczenie')

class CreateAccountRequestForm(FlaskForm):
    email = SelectField('User', choices=[])
    submit_button = SubmitField('Przypisz użytkownika')


class SolutionForm(FlaskForm):
    email = StringField('Student', render_kw={'readonly': True})
    points = FloatField('Punkty')
    is_approved = BooleanField('Zaakceptowano')
    file_path = StringField('file', render_kw={'readonly': True})
    attempt = IntegerField('attempt', render_kw={'readonly': True})
    ip_address = StringField('ip address', render_kw={'readonly': True})
    os_info = StringField('os info', render_kw={'readonly': True})
    submit = SubmitField('Zapisz')

class SolutionsForm(FlaskForm):
    title = StringField('title')
    solutions = FieldList(FormField(SolutionForm))
    submit = SubmitField('Zapisz')

