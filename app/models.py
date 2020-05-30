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
    link = db.Column(db.String(60), unique=True)

    def get_directory(self):
        return os.path.join(current_app.instance_path, self.name)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    user_exercises = db.relationship('UserExercises', backref='author', lazy='dynamic')
    courses = db.relationship('Course', secondary=user_course_assoc, backref='member')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_admin(self):
        return self.role == Role.ADMIN


class Role:
    ADMIN = 'ADMIN'
    STUDENT = 'STUDENT'


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
    exercise_templates = db.relationship('ExerciseTemplate', backref='lesson', lazy='dynamic')

    def get_directory(self):
        return os.path.join(current_app.instance_path, self.course.name, self.name)


class ExerciseTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    content = db.Column(db.String(500))
    max_points = db.Column(db.Float)
    end_date = db.Column(db.DATE)
    max_attempts = db.Column(db.Integer, default=3)
    tests = db.relationship('Tests', backref='template', lazy='dynamic')
    output_path = db.Column(db.String(100))
    input_path = db.Column(db.String(100))
    solutions = db.relationship('UserExercises', backref='template', lazy='dynamic')

    def get_directory(self):
        return os.path.join(self.lesson.get_directory(), self.name)


class Tests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_template_id = db.Column(db.ForeignKey('exercise_template.id'))
    output_path = db.Column(db.String(100))
    input_path = db.Column(db.String(100))
    points = db.Column(db.Float)


class UserExercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_template_id = db.Column(db.ForeignKey('exercise_template.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Float)
    file_path = db.Column(db.String(100))
    attempt = db.Column(db.Integer)
    is_approved = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(20))
    os_info = db.Column(db.String(50))

    def get_directory(self):
        return os.path.join(self.template.get_directory(), self.author.email.split('@')[0], str(self.attempt))
