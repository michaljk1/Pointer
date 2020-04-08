from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import DateField


class UploadForm(FlaskForm):
    file = FileField('Select File')
    submit_button = SubmitField('Submit Form')


class CourseForm(FlaskForm):
    name = StringField('Course name')
    submit_button = SubmitField('Add course')


class LessonForm(FlaskForm):
    name = StringField('Lesson name')
    text_content = StringField('Content')
    pdf_content = FileField('Select File')
    url_content = StringField('Url')
    submit_button = SubmitField('Add Lesson')


class TemplateForm(FlaskForm):
    content = StringField('content')
    end_date = DateField('End date', format='%Y-%m-%d')
    submit_button = SubmitField('Add template')
