# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, \
    ValidationError, TextAreaField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional

from app.models.usercourse import Course
from app.student.student_forms import SolutionStudentSearchForm


class CourseForm(FlaskForm):
    name = StringField('Nazwa kursu', validators=[Length(min=1, message="Wprowadź nazwę")])
    submit_button = SubmitField('Zapisz')

    def validate_name(self, name):
        courses = Course.query.all()
        replaced_name = name.data.replace(" ", "_").lower()
        if '/' in name.data:
            raise ValidationError('Wprowadzono niepoprawny znak - /.')
        for course in courses:
            if course.name.replace(" ", "_").lower() == replaced_name:
                raise ValidationError('Podana nazwa kursu jest już zajęta.')
        if name.data.lower() == 'all':
            raise ValidationError('Podana nazwa kursu nie jest dostępna.')


class EditLessonForm(FlaskForm):
    pdf_content = FileField('Wybierz plik')
    submit_button = SubmitField('Zapisz')


class LessonForm(FlaskForm):
    name = StringField('Nazwa lekcji', validators=[DataRequired()])
    pdf_content = FileField('Wybierz plik')
    submit_button = SubmitField('Dodaj lekcję')

    def validate_name(self, name):
        if '/' in name.data:
            raise ValidationError('Wprowadzono niepoprawny znak - /.')


class ExerciseEditForm(FlaskForm):
    max_attempts = IntegerField('Liczba prób', default=3, validators=[DataRequired()])
    end_date = DateField('Data końcowa', format='%Y-%m-%d', validators=[DataRequired()])
    end_time = TimeField('Godzina')
    compile_command = StringField('Kompilacja')
    run_command = StringField('Uruchamianie', validators=[DataRequired()])
    program_name = StringField('Nazwa testowanego pliku', validators=[DataRequired()])
    timeout = IntegerField('Timeout(sekundy)')
    interval = IntegerField('Przerwa pomiędzy wysłaniem zadań(sekundy)')
    submit_button = SubmitField('Zapisz')


class ExerciseForm(ExerciseEditForm):
    name = StringField('Nazwa', validators=[DataRequired()])
    output = FileField('Output', validators=[DataRequired()])
    input = FileField('Input', validators=[DataRequired()])
    max_points = FloatField('Liczba punktów', validators=[DataRequired()])
    submit_button = SubmitField('Dodaj ćwiczenie')

    def validate_name(self, name):
        if '/' in name.data:
            raise ValidationError('Wprowadzono niepoprawny znak - /.')

    def validate_input(self, input):
        if input.data.filename.rsplit('.', 1)[1].lower() != 'txt':
            raise ValidationError('Oczekiwany format - .txt')

    def validate_output(self, output):
        if output.data.filename.rsplit('.', 1)[1].lower() != 'txt':
            raise ValidationError('Oczekiwany format - .txt')


class TestForm(FlaskForm):
    max_points = FloatField('Liczba punktów', validators=[DataRequired()])
    output = FileField('Output', validators=[DataRequired()])
    input = FileField('Input', validators=[DataRequired()])
    submit_button = SubmitField('Dodaj test')

    def validate_input(self, input):
        if input.data.filename.rsplit('.', 1)[1].lower() != 'txt':
            raise ValidationError('Oczekiwany format - .txt')

    def validate_output(self, output):
        if output.data.filename.rsplit('.', 1)[1].lower() != 'txt':
            raise ValidationError('Oczekiwany format - .txt')


class EmailForm(FlaskForm):
    email = SelectField('Email', choices=[])


class AddStudentForm(EmailForm):
    submit_button = SubmitField('Przypisz studenta')


class DeleteStudentForm(EmailForm):
    submit_button = SubmitField('Usuń studenta')


class StatisticsForm(FlaskForm):
    course = SelectField('Kurs', choices=[['ALL', 'Dowolny']], validators=[DataRequired()])
    email = SelectField('Student', choices=[['ALL', 'Dowolny']], validators=[DataRequired()])
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
    comment = TextAreaField('Komentarz', render_kw={'rows': '5'})
    submit_comment = SubmitField('Dodaj komentarz')
    submit_points = SubmitField('Zmień punktację')


class SolutionAdminSearchForm(SolutionStudentSearchForm):
    is_published = BooleanField('Tylko opublikowane zadania', default=True)
    points_from = FloatField('Punkty od', [Optional()])
    points_to = FloatField('Punkty do', [Optional()])
    email = StringField('Email')
    index = StringField('Indeks')
    name = StringField('Imię')
    surname = StringField('Nazwisko')
    ip_address = StringField('IP')
