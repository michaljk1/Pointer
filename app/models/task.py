import redis
import rq
from flask import current_app

from app import db


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    task_type = db.Column(db.String(20))
    complete = db.Column(db.Boolean, default=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    Type = {
        'EMAIL': 'Email',
        'SOLUTION': 'Solution'
    }

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except redis.exceptions.RedisError:
            return None
        return rq_job
