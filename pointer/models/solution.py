import os
from datetime import datetime
from pointer import db
from pointer.DefaultUtil import get_current_date


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_date = db.Column(db.DateTime)
    points = db.Column(db.Float, nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    attempt = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)
    os_info = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    details = db.Column(db.TEXT)
    Status = {
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
