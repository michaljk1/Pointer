import sys

from app import create_app, db
from app.services.ExerciseService import execute_solution

app = create_app()
app.app_context().push()


def point_solution(solution_id):
    try:
        execute_solution(solution_id)
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())