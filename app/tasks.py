import sys

from rq import get_current_job

from app import create_app, db
from app.models.task import Task
from app.services.ExerciseService import execute_solution

app = create_app()
app.app_context().push()


def point_solution(solution_id):
    try:
        _set_task_progress(0)
        execute_solution(solution_id)
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.description = 'progress'
        if progress >= 100:
            task.complete = True
        db.session.commit()
