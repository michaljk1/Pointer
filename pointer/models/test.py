import os

from pointer import db


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    output_name = db.Column(db.String(100))
    input_name = db.Column(db.String(100))
    points = db.Column(db.Float)
    order = db.Column(db.Integer)

    def get_directory(self):
        return os.path.join(self.executor.get_directory(), 'tests', 'test'+str(self.id))

    def get_course(self):
        return self.executor.get_course()