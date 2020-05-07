from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField


class UploadForm(FlaskForm):
    file = FileField('Select File')
    submit_button = SubmitField('Submit Form')
