import os
import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from pointer import db, login
from pointer.models.exercise import Exercise

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

    def get_students(self):
        return [student for student in self.members if student.role == role['STUDENT']]

    def get_directory(self):
        return os.path.join(current_app.instance_path, self.name.replace(" ", "_"))

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

    def get_lesson_by_name(self, name):
        for lesson in self.lessons:
            if lesson.name == name:
                return lesson
        return None

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
    index = db.Column(db.String(30), index=True, unique=True)
    login = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
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

    def get_solutions_with_points_for_student(self, course: Course):
        user_points, user_exercises = 0.0, []
        for exercise in course.get_exercises():
            user_solution = exercise.get_user_active_solution(user_id=self.id)
            if user_solution is not None and exercise.is_finished():
                user_exercises.append(UserExercise(exercise=exercise, points=user_solution.points))
                user_points += user_solution.points
            else:
                user_exercises.append(UserExercise(exercise=exercise, points=0.0))
        return user_exercises, user_points

    def get_solutions_with_points_for_admin(self, course: Course):
        user_points, user_exercises = 0.0, []
        for exercise in course.get_exercises():
            user_solution = exercise.get_user_active_solution(user_id=self.id)
            if user_solution is not None:
                user_exercises.append(UserExercise(exercise=exercise, points=user_solution.points))
                user_points += user_solution.points
            else:
                user_exercises.append(UserExercise(exercise=exercise, points=0.0))
        return user_exercises, user_points

    def get_admin_directory(self):
        if self.role == role['ADMIN']:
            return os.path.join(current_app.instance_path, self.login)
        return None

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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserExercise:
    def __init__(self, exercise: Exercise, points: float):
        self.exercise = exercise
        self.points = points
        self.course = exercise.get_course()
        self.lesson = exercise.lesson
        self.max_points = exercise.get_max_points()

    def get_percent_value(self):
        if self.max_points > 0:
            return round((self.points / self.max_points * 100), 2)
        else:
            return float(0)


role = {
    'ADMIN': 'ADMIN',
    'STUDENT': 'STUDENT',
    'MODERATOR': 'MODERATOR'
}
