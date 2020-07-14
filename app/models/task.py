import redis
import rq
from flask import current_app

from app import db


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except redis.exceptions.RedisError:
            return None
        return rq_job
