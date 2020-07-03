from flask_wtf.file import FileField
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, \
    ValidationError, TextAreaField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional
from pointer.models.usercourse import Course
from pointer.student.forms import SolutionStudentSearchForm


class UploadForm(FlaskForm):
    file = FileField('Wybierz plik')
    submit_button = SubmitField('Zapisz')


class CourseForm(FlaskForm):
    name = StringField('Nazwa kursu', validators=[Length(min=1, message="Wprowadź nazwę")])
    submit_button = SubmitField('Dodaj kurs')

    def validate_name(self, name):
        courses = Course.query.all()
        replaced_name = name.data.replace(" ", "_")
        for course in courses:
            if course.name.replace(" ", "_") == replaced_name:
                raise ValidationError('Podana nazwa kursu jest już zajęta.')


class EditLessonForm(FlaskForm):
    text_content = TextAreaField('Treść', render_kw={'cols': '40', 'rows': '13'},
                                 validators=[DataRequired()])
    pdf_content = FileField('Wybierz plik')
    submit_button = SubmitField('Edytuj lekcję')


class LessonForm(FlaskForm):
    name = StringField('Nazwa lekcji', validators=[DataRequired()])
    text_content = TextAreaField('Treść', render_kw={'cols': '40', 'rows': '13'},
                                 validators=[DataRequired()])
    pdf_content = FileField('Wybierz plik')
    submit_button = SubmitField('Dodaj lekcję')


class ExerciseForm(FlaskForm):
    name = StringField('Nazwa', validators=[DataRequired()])
    content = StringField('Treść', validators=[DataRequired()])
    max_attempts = IntegerField('Liczba prób', default=3, validators=[DataRequired()])
    end_date = DateField('Data końcowa', format='%Y-%m-%d', validators=[DataRequired()])
    end_time = TimeField('Godzina')
    compile_command = StringField('compile command')
    run_command = StringField('run_command', validators=[DataRequired()])
    output = FileField('Output', validators=[DataRequired()])
    input = FileField('Input', validators=[DataRequired()])
    max_points = FloatField('Liczba punktów', validators=[DataRequired()])
    program_name = StringField('Nazwa testowanego pliku', validators=[DataRequired()])
    timeout = IntegerField('Timeout w sekundach')
    interval = IntegerField('Przerwa pomiędzy wysłaniem zadań')
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
    search_button = SubmitField('Wyszukaj')


class CSVForm(FlaskForm):
    submit_button = SubmitField('Eksport CSV')


class StatisticsUserForm(FlaskForm):
    email = SelectField('Użytkownik', choices=[])
    search_button = SubmitField('Wyszukaj')


class SolutionForm(FlaskForm):
    email = StringField('Student', render_kw={'readonly': True})
    error_msg = TextAreaField('Szczegóły błędu', render_kw={'rows': '10'})
    points = FloatField('Punkty')
    status = StringField('Status')
    admin_ref = BooleanField('Odrzuć zadanie')
    file_path = StringField('Plik', render_kw={'readonly': True})
    attempt = IntegerField('Próba', render_kw={'readonly': True})
    ip_address = StringField('ip address', render_kw={'readonly': True})
    os_info = StringField('os info', render_kw={'readonly': True})
    submit = SubmitField('Zmień punktację')



class SolutionAdminSearchForm(SolutionStudentSearchForm):
    points_from = FloatField('Punkty od', [Optional()])
    points_to = FloatField('Punkty do', [Optional()])
    name = StringField('Imię')
    surname = StringField('Nazwisko')
