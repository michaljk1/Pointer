import os
from sqlalchemy.dialects.mysql import LONGTEXT
from pointer import db
from pointer.DateUtil import get_current_date


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_date = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Float, nullable=False, default=0)
    file_path = db.Column(db.String(100), nullable=False)
    attempt = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)
    os_info = db.Column(LONGTEXT, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Oddano')
    error_msg = db.Column(LONGTEXT)
    comment = db.Column(LONGTEXT)
    Status = {
        'SEND': 'Oddano',
        'REFUSED': 'Odrzucono',
        'ALL': 'Dowolny',
        'APPROVED': 'Zaakceptowano',
        'COMPILE_ERROR': 'Error - kompilacja',
        'TEST_ERROR': 'Error - testowanie',
        'ERROR': 'Error',
        'NOT_ACTIVE': 'Nieaktywne'
    }

    def get_student_status(self):
        if not self.exercise.is_finished() and self.status in [self.Status['APPROVED'], self.Status['REFUSED'],
                                                               self.Status['NOT_ACTIVE']]:
            return self.Status['NOT_ACTIVE']
        else:
            return self.status

    def get_student_points(self):
        if self.exercise.is_finished():
            return self.points
        else:
            return '-'

    def get_lesson(self):
        return self.exercise.lesson

    def get_course(self):
        return self.exercise.lesson.course

    def get_directory(self):
        return os.path.join(self.exercise.get_directory(), self.author.login, str(self.attempt))
