# -*- coding: utf-8 -*-
import os

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.datastructures import FileStorage
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app import db, login
from app.models.lesson import Lesson
from app.models.task import Task
from app.services.FileUtil import create_directory

user_course_assoc = db.Table('user_courses',
                             db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                             db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
                             )


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')
    link = db.Column(db.String(25), unique=True)
    is_open = db.Column(db.Boolean, default=True)

    def add_lesson(self, lesson_name, file: FileStorage, content):
        filename = secure_filename(file.filename)
        if filename == '':
            filename = None
        new_lesson = Lesson(name=lesson_name, content_pdf_path=filename, content_text=content)
        self.lessons.append(new_lesson)
        lesson_directory = new_lesson.get_directory()
        create_directory(lesson_directory)
        if filename is not None:
            file.save(os.path.join(lesson_directory, filename))
        return new_lesson

    def get_students(self):
        return [student for student in self.members if student.role == User.Roles['STUDENT']]

    def get_directory(self):
        return os.path.join(current_app.config['INSTANCE_DIR'], 'courses', self.name.replace(" ", "_"))

    def get_exercises(self):
        exercises = []
        for lesson in self.lessons:
            exercises += lesson.get_exercises()
        return exercises

    def is_lesson_name_proper(self, lesson_name):
        lesson_name = lesson_name.replace(" ", "_").lower()
        for lesson in self.lessons:
            if lesson.name.replace(" ", "_").lower() == lesson_name:
                return False
        return True

    def get_course_points(self):
        points = 0.0
        for lesson in self.lessons:
            for exercise in lesson.exercises:
                if exercise.is_published:
                    points += exercise.get_max_points()
        return points


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), index=True, unique=True)
    password = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    history_logins = db.relationship('LoginInfo', backref='user', lazy='dynamic')
    Roles = {
        'ADMIN': 'ADMIN',
        'STUDENT': 'STUDENT',
        'TEACHER': 'TEACHER'
    }

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        "polymorphic_on": role
    }

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_teacher(self):
        return self.role == User.Roles['TEACHER']

    def is_admin(self):
        return self.role == User.Roles['ADMIN']

    def is_student(self):
        return self.role == User.Roles['STUDENT']

    @staticmethod
    def verify_confirm_email_token(token):
        try:
            email = jwt.decode(token, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])['confirm_email']
        except:
            return
        return User.query.filter_by(email=email).first()

    @staticmethod
    def verify_reset_password_token(token):
        try:
            email = jwt.decode(token, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.filter_by(email=email).first()

    def launch_email(self, name, description):
        rq_job = current_app.email_queue.enqueue('app.redis_tasks.' + name, self.email)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    task_type=Task.Type['EMAIL'], user=self)
        db.session.add(task)
        db.session.commit()
        return task


class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'ADMIN'
    }


class UserCourse(User):
    index = db.Column(db.String(30), index=True, unique=True)
    solutions = db.relationship('Solution', backref='author', lazy='dynamic')
    courses = db.relationship('Course', secondary=user_course_assoc, backref='members')

    def get_course_names(self):
        course_names = []
        for course in self.courses:
            course_names.append(course.name)
        return course_names

    def get_directory(self):
        return os.path.join(current_app.config['INSTANCE_DIR'], 'teachers', self.index)

    def launch_course_email(self, course):
        rq_job = current_app.email_queue.enqueue('app.redis_tasks.send_course_email', self.email, course, self.role)
        task = Task(id=rq_job.get_id(), name='send_course_email', description='append course',
                    task_type=Task.Type['EMAIL'], user=self)
        db.session.add(task)
        db.session.commit()
        return task


class Teacher(UserCourse):
    exports = db.relationship('Export', backref='user', lazy='dynamic')
    __mapper_args__ = {
        'polymorphic_identity': 'TEACHER',
    }


class Student(UserCourse):
    __mapper_args__ = {
        'polymorphic_identity': 'STUDENT',
    }


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
