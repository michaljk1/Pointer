from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, \
    ValidationError
from wtforms.fields.html5 import DateField

from app.models import Course, Lesson
from app.student.forms import SolutionStudentSearchForm


class UploadForm(FlaskForm):
    file = FileField('Wybierz plik')
    submit_button = SubmitField('Zapisz')


class CourseForm(FlaskForm):
    name = StringField('Nazwa kursu')
    submit_button = SubmitField('Dodaj kurs')

    def validate_name(self, name):
        course = Course.query.filter_by(name=name.data).first()
        if course is not None:
            raise ValidationError('Podana nazwa kursu jest już zajęta.')


class LessonForm(FlaskForm):
    name = StringField('Nazwa lekcji')
    text_content = StringField('Treść')
    pdf_content = FileField('Wybierz plik')
    content_url = StringField('Link')
    submit_button = SubmitField('Dodaj lekcję')

    def validate_name(self, name):
        for lesson in Lesson.query.all():
            if lesson.name.replace(" ", "_") == name.data.replace(" ", "_"):
                raise ValidationError('Podana nazwa lekcji jest już zajęta')


class TemplateForm(FlaskForm):
    name = StringField('Nazwa')
    content = StringField('Treść')
    max_attempts = IntegerField('Liczba prób', default=3)
    max_points = FloatField('Liczba punktów')
    end_date = DateField('Termin końcowy', format='%Y-%m-%d')
    compile_command = StringField('compile command')
    run_command = StringField('run_command')
    output = FileField('Output')
    input = FileField('Input')
    program_name = StringField('Nazwa testowanego pliku')
    submit_button = SubmitField('Dodaj ćwiczenie')


class CreateAccountRequestForm(FlaskForm):
    email = SelectField('Użytkownik', choices=[])
    submit_button = SubmitField('Przypisz użytkownika')


class SolutionForm(FlaskForm):
    email = StringField('Student', render_kw={'readonly': True})
    points = FloatField('Punkty')
    admin_refused = BooleanField('Odrzuć zadanie')
    file_path = StringField('Plik', render_kw={'readonly': True})
    attempt = IntegerField('Próba', render_kw={'readonly': True})
    ip_address = StringField('ip address', render_kw={'readonly': True})
    os_info = StringField('os info', render_kw={'readonly': True})
    submit = SubmitField('Zapisz')


class SolutionAdminSearchForm(SolutionStudentSearchForm):
    name = StringField('Imię')
    surname = StringField('Nazwisko')
