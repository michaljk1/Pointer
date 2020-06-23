import os

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import db, login

user_course_assoc = db.Table(
    'user_courses',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')
    link = db.Column(db.String(25), unique=True)
    is_open = db.Column(db.Boolean, default=True)

    def get_directory(self):
        return os.path.join(current_app.instance_path, self.name.replace(" ", "_"))

    def get_lesson_by_name(self, name):
        for lesson in self.lessons:
            if lesson.name == name:
                return lesson
        return None


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), index=True, unique=True)
    login = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    solutions = db.relationship('Solution', backref='author', lazy='dynamic')
    courses = db.relationship('Course', secondary=user_course_assoc, backref='members')
    history_logins = db.relationship('LoginInfo', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_admin(self):
        return self.role == role['ADMIN']

    def is_moderator(self):
        return self.role == role['MODERATOR']

    def is_student(self):
        return self.role == role['STUDENT']

    def get_course_names(self):
        course_names = []
        for course in self.courses:
            course_names.append(course.name)
        return course_names

    def get_student_ids(self):
        pass


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


role = {
    'ADMIN': 'ADMIN',
    'STUDENT': 'STUDENT',
    'MODERATOR': 'MODERATOR'
}


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    raw_text = db.Column(db.String(600))
    content_pdf_path = db.Column(db.String(100))
    content_url = db.Column(db.String(100))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    exercises = db.relationship('Exercise', backref='lesson', lazy='dynamic')

    def get_directory(self):
        return os.path.join(self.course.get_directory(), self.name.replace(" ", "_"))


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    content = db.Column(db.String(500))
    end_date = db.Column(db.DateTime)
    max_attempts = db.Column(db.Integer, default=3)
    program_name = db.Column(db.String(50))
    compile_command = db.Column(db.String(100))
    run_command = db.Column(db.String(100))
    timeout = db.Column(db.Integer, default=0, nullable=False)
    solutions = db.relationship('Solution', backref='exercise', lazy='dynamic')
    tests = db.relationship('Test', backref='executor', lazy='dynamic')

    def get_course(self):
        return self.lesson.course

    def get_directory(self):
        return os.path.join(self.lesson.get_directory(), self.name.replace(" ", "_"))

    def get_max_points(self):
        max_points = 0
        for test in self.tests:
            max_points += test.points
        return max_points

    def get_user_solutions(self, user_id):
        user_solutions = []
        for solution in self.solutions:
            if solution.user_id == user_id:
                user_solutions.append(solution)
        return user_solutions

    def get_max_points(self):
        points = 0
        for test in self.tests:
            points += test.points
        return points

    def create_test(self, input_file, output_file, points):
        input_name, output_name = secure_filename(input_file.filename), secure_filename(output_file.filename)
        test = Test(points=points, input_name=input_name, output_name=output_name, exercise_id=self.id,
                    order=len(self.tests.all()))
        self.tests.append(test)
        test_directory = test.get_directory()
        os.makedirs(test_directory)
        input_file.save(os.path.join(test_directory, input_name))
        output_file.save(os.path.join(test_directory, output_name))


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    output_name = db.Column(db.String(100))
    input_name = db.Column(db.String(100))
    points = db.Column(db.Float)
    order = db.Column(db.Integer)

    def get_directory(self):
        return os.path.join(self.executor.get_directory(), str(self.order))


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_date = db.Column(db.DateTime)
    points = db.Column(db.Float, nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    attempt = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(20), nullable=False)
    os_info = db.Column(db.String(150), nullable=False)
    admin_refused = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False)
    solutionStatus = {
        'SEND': 'Oddano',
        'REFUSED': 'Odrzucono',
        'ACTIVE': 'Aktywne',
        'ALL': 'Status',
        'COMPILE_ERROR': 'Błąd kompilacji',
        'RUN_ERROR': 'Błąd uruchomienia',
        'ERROR': 'Error',
        'NOT_ACTIVE': 'Nieaktywne'
    }

    def get_lesson(self):
        return self.exercise.lesson

    def get_course(self):
        return self.exercise.lesson.course

    def get_directory(self):
        return os.path.join(self.exercise.get_directory(), self.author.login, str(self.attempt))


class LoginInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ip_address = db.Column(db.String(40), nullable=False)
    login_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)
    loginStatus = {
        'SUCCESS': 'Success',
        'ERROR': 'Error',
        'ALL': 'All'
    }


class SolutionExport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(100))
    type = db.Column(db.String(10))
    generation_date = db.Column(db.DateTime)
    types = {
        'CSV': 'csv',
        'PDF': 'pdf'
    }

    def get_directory(self):
        user = User.query.filter_by(id=self.user_id).first()
        return os.path.join(current_app.instance_path, user.login)

