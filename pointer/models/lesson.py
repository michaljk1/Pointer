import os

from pointer import db


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    raw_text = db.Column(db.String(600))
    content_pdf_path = db.Column(db.String(100))
    content_url = db.Column(db.String(100))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    exercises = db.relationship('Exercise', backref='lesson', lazy='dynamic')

    def get_directory(self):
        return os.path.join(self.course.get_directory(), self.name.replace(" ", "_"))

    def is_exercise_name_proper(self, exercise_name):
        for exercise in self.exercises:
            if exercise.name.replace(" ", "_") == exercise_name.replace(" ", "_"):
                return False
        return True
