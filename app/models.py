import os

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), index=True, unique=True)
    login = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    solutions = db.relationship('Solutions', backref='author', lazy='dynamic')
    courses = db.relationship('Course', secondary=user_course_assoc, backref='member')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_moderator(self):
        return self.role == Role.MODERATOR

    def is_student(self):
        return self.role == Role.STUDENT


class Role:
    ADMIN = 'ADMIN'
    STUDENT = 'STUDENT'
    MODERATOR = 'MODERATOR'


class SolutionStatus:
    SEND = 'Oddano'
    REFUSED = 'Odrzucono'
    ACTIVE = 'Aktywne'
    ALL = 'Status'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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
    max_points = db.Column(db.Float)
    end_date = db.Column(db.DATE)
    max_attempts = db.Column(db.Integer, default=3)
    output_name = db.Column(db.String(100))
    input_name = db.Column(db.String(100))
    program_name = db.Column(db.String(50))
    compile_command = db.Column(db.String(30))
    run_command = db.Column(db.String(30))
    solutions = db.relationship('Solutions', backref='exercise', lazy='dynamic')
    tests = db.relationship('Test', backref='executor', lazy='dynamic')

    def get_course(self):
        return self.lesson.course

    def get_directory(self):
        return os.path.join(self.lesson.get_directory(), self.name.replace(" ", "_"))

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


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    output_name = db.Column(db.String(100))
    input_name = db.Column(db.String(100))
    points = db.Column(db.Float)


class Solutions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_date = db.Column(db.DATE)
    points = db.Column(db.Float, nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    attempt = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(20), nullable=False)
    os_info = db.Column(db.String(150), nullable=False)
    admin_refused = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False)

    def get_course(self):
        return self.exercise.lesson.course

    def get_directory(self):
        return os.path.join(self.exercise.get_directory(), self.author.login, str(self.attempt))
