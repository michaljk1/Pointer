from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import DateField


class UploadForm(FlaskForm):
    file = FileField('Select File')


class CourseForm(FlaskForm):
    name = StringField('Course name')


class LessonForm(FlaskForm):
    name = StringField('Lesson name')
    text_content = StringField('Content')
    pdf_content = FileField('Select File')
    url_content = StringField('Url')


class TemplateForm(FlaskForm):
    content = StringField('content')
    end_date = DateField('DatePicker', format='%Y-%m-%d')

