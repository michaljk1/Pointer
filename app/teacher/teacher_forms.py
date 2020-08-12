# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, BooleanField, SubmitField, IntegerField, FloatField, SelectField, \
    ValidationError, TextAreaField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

from app.default.default_forms import EmailForm
from app.models.usercourse import Course
from app.student.student_forms import SolutionStudentSearchForm


class CourseForm(FlaskForm):
    name = StringField('Nazwa kursu', validators=[DataRequired(), Length(max=60,
                                                                         message='Nazwa kursu musi być krótsza niż 60 znaków.')])
    submit_button = SubmitField('Dodaj kurs')

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
    submit_button = SubmitField('Zapisz zmiany')

    def validate_pdf_content(self, pdf_content):
        if pdf_content.data is not None and pdf_content.data.filename.rsplit('.', 1)[1].lower() != 'pdf':
            flash('Oczekiwany format pliku - .pdf', 'error')
            raise ValidationError('Oczekiwany format - .pdf')


class LessonForm(EditLessonForm):
    name = StringField('Nazwa lekcji', validators=[DataRequired(), Length(max=60,
                                                                          message='Nazwa lekcji musi być krótsza niż 60 znaków.')])
    submit_button = SubmitField('Dodaj lekcję')

    def validate_name(self, name):
        if '/' in name.data:
            raise ValidationError('Wprowadzono niepoprawny znak - /.')


class ExerciseEditForm(FlaskForm):
    max_attempts = IntegerField('Liczba prób', default=3, validators=[DataRequired()])
    end_date = DateField('Data końcowa', format='%Y-%m-%d', validators=[DataRequired()])
    end_time = TimeField('Godzina')
    compile_command = StringField('Kompilacja', validators=[
        Length(max=100, message='Komenda kompilacji musi być krótsza niż 100 znaków.')])
    run_command = StringField('Uruchamianie', validators=[DataRequired(), Length(max=100,
                                                                                 message='Komenda uruchomienia musi być krótsza niż 100 znaków.')])
    program_name = StringField('Nazwa testowanego pliku', validators=[DataRequired(), Length(max=50,
                                                                                             message='Nazwa programu musi być krótsza niż 50 znaków.')])
    interval = IntegerField('Przerwa pomiędzy wysłaniem zadań(sekundy)', default=100,
                            validators=[NumberRange(min=0, max=86400,
                                                    message='Wartość musi znajdować się w przedziale od 0 do 86400.')])
    submit_button = SubmitField('Zapisz zmiany')


class ExerciseForm(ExerciseEditForm):
    name = StringField('Nazwa', validators=[DataRequired(), Length(max=60,
                                                                   message='Nazwa zadania musi być krótsza niż 60 znaków.')])
    submit_button = SubmitField('Dodaj zadanie')

    def validate_name(self, name):
        if '/' in name.data:
            raise ValidationError('Wprowadzono niepoprawny znak - /.')


class TestForm(FlaskForm):
    max_points = FloatField('Liczba punktów', validators=[DataRequired(), NumberRange(min=0, max=100000,
                                                                                      message='Wartość musi znajdować się w przedziale od 0 do 100000.')])
    timeout = IntegerField('Timeout(sekundy)', default=600, validators=[DataRequired(), NumberRange(min=0, max=86400,
                                                                                                    message='Wartość musi znajdować się w przedziale od 0 do 86400.')])
    output = FileField('Output', validators=[DataRequired()])
    input = FileField('Input', validators=[DataRequired()])
    submit_button = SubmitField('Dodaj test')

    def validate_input(self, input):
        if input.data.filename.rsplit('.', 1)[1].lower() != 'txt':
            raise ValidationError('Oczekiwany format - .txt')

    def validate_output(self, output):
        if output.data.filename.rsplit('.', 1)[1].lower() != 'txt':
            raise ValidationError('Oczekiwany format - .txt')


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
    teacher_ref = BooleanField('Odrzuć zadanie')
    file_path = StringField('Plik', render_kw={'readonly': True})
    attempt = IntegerField('Próba', render_kw={'readonly': True})
    ip_address = StringField('Adres IP', render_kw={'readonly': True})
    os_info = StringField('Przeglądarka', render_kw={'readonly': True})
    comment = TextAreaField('Komentarz', render_kw={'rows': '5'})
    submit_comment = SubmitField('Dodaj komentarz')
    submit_points = SubmitField('Zmień punktację')


class SolutionTeacherSearchForm(SolutionStudentSearchForm):
    is_published = BooleanField('Tylko opublikowane zadania', default=True)
    points_from = FloatField('Punkty od', [Optional()])
    points_to = FloatField('Punkty do', [Optional()])
    email = StringField('Email')
    index = StringField('Indeks')
    name = StringField('Imię')
    surname = StringField('Nazwisko')
    ip_address = StringField('IP')
