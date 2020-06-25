import os

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
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

    def get_course_points(self):
        points = 0
        for lesson in self.lessons:
            for exercise in lesson.exercises:
                points += exercise.get_max_points()
        return points

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

    def get_points_student(self, course: Course):
        user_points = 0
        for solution in self.solutions:
            if solution.get_course() == course and solution.status == solution.Status['ACTIVE'] and solution.is_visible():
                user_points += solution.points
        return user_points

    def get_points_admin(self, course: Course):
        user_points = 0
        for solution in self.solutions:
            if solution.get_course() == course and solution.status == solution.Status['ACTIVE']:
                user_points += solution.points
        return user_points


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


role = {
    'ADMIN': 'ADMIN',
    'STUDENT': 'STUDENT',
    'MODERATOR': 'MODERATOR'
}
