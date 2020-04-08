from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    roles = db.relationship('Role', secondary='user_roles')
    user_exercises = db.relationship('UserExercises', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')


class CourseUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    raw_text = db.Column(db.String(600))
    content_pdf_path = db.Column(db.String(100))
    content_url = db.Column(db.String(100))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    exercise_templates = db.relationship('ExerciseTemplate', backref='template', lazy='dynamic')


class ExerciseTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    content = db.Column(db.String(500))
    points = db.Column(db.Float)
    end_date = db.Column(db.DATE)
    max_attempts = db.Column(db.Integer, default=3)
    test_path = db.Column(db.String(100))


class UserExercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_template_id = db.Column(db.ForeignKey('exercise_template.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_path = db.Column(db.String(100))
    attempt = db.Column(db.Integer)
    is_approved = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(20))
    browser_info = db.Column(db.String(50))
    os_info = db.Column(db.String(50))
