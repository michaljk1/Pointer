from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, \
    ValidationError
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired
from app.models.usercourse import Course
from app.models.lesson import Lesson
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
    name = StringField('Nazwa lekcji', validators=[DataRequired()])
    text_content = StringField('Treść', validators=[DataRequired()])
    pdf_content = FileField('Wybierz plik')
    content_url = StringField('Link')
    submit_button = SubmitField('Dodaj lekcję')

    def validate_name(self, name):
        for lesson in Lesson.query.all():
            if lesson.name.replace(" ", "_") == name.data.replace(" ", "_"):
                raise ValidationError('Podana nazwa lekcji jest już zajęta')


class ExerciseForm(FlaskForm):
    name = StringField('Nazwa', validators=[DataRequired()])
    content = StringField('Treść', validators=[DataRequired()])
    max_attempts = IntegerField('Liczba prób', default=3, validators=[DataRequired()])
    end_date = DateField('Data końcowa', format='%Y-%m-%d', validators=[DataRequired()] )
    end_time = TimeField('Godzina')
    compile_command = StringField('compile command')
    run_command = StringField('run_command' , validators=[DataRequired()])
    output = FileField('Output', validators=[DataRequired()])
    input = FileField('Input', validators=[DataRequired()])
    max_points = FloatField('Liczba punktów', validators=[DataRequired()])
    program_name = StringField('Nazwa testowanego pliku', validators=[DataRequired()])
    timeout = IntegerField('Timeout w sekundach')
    submit_button = SubmitField('Dodaj ćwiczenie')


class TestForm(FlaskForm):
    max_points = FloatField('Liczba punktów', validators=[DataRequired()])
    output = FileField('Output', validators=[DataRequired()])
    input = FileField('Input', validators=[DataRequired()])
    submit_button = SubmitField('Dodaj test')


class AssigneUserForm(FlaskForm):
    email = SelectField('Użytkownik', choices=[])
    submit_button = SubmitField('Przypisz użytkownika')


class StatisticsCourseForm(FlaskForm):
    course = SelectField('Kurs', choices=[])
    submit_button = SubmitField('Wyszukaj')

class StatisticsUserForm(FlaskForm):
    email = SelectField('Użytkownik', choices=[])
    submit_button = SubmitField('Wyszukaj')


class EnableAssingmentLink(FlaskForm):
    activate = BooleanField('Aktywny zapis')
    submit_button = SubmitField('Zapisz')


class SolutionForm(FlaskForm):
    email = StringField('Student', render_kw={'readonly': True})
    points = FloatField('Punkty')
    admin_ref = BooleanField('Odrzuć zadanie')
    file_path = StringField('Plik', render_kw={'readonly': True})
    attempt = IntegerField('Próba', render_kw={'readonly': True})
    ip_address = StringField('ip address', render_kw={'readonly': True})
    os_info = StringField('os info', render_kw={'readonly': True})
    submit = SubmitField('Zapisz')


class SolutionAdminSearchForm(SolutionStudentSearchForm):
    name = StringField('Imię')
    surname = StringField('Nazwisko')
