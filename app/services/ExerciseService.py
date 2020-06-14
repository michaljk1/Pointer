import os
import subprocess

from app import db
from app.models import Solutions, User, Course, Lesson, ExerciseTemplate, SolutionStatus


class ExerciseService:
    @staticmethod
    def accept_best_solution(user_id, exercise):
        user_exercises = Solutions.query.filter_by(user_id=user_id, exercise_template_id=exercise.id).all()
        points = 0
        best_solution = None
        for user_exercise in user_exercises:
            if user_exercise.status != SolutionStatus.REFUSED and user_exercise.points >= points:
                best_solution = user_exercise
                points = best_solution.points
        if best_solution is not None:
            best_solution.status = SolutionStatus.ACTIVE
            user_exercises.remove(best_solution)
        for user_exercise in user_exercises:
            if user_exercise.status != SolutionStatus.REFUSED:
                user_exercise.status = SolutionStatus.SEND
        db.session.commit()

    @staticmethod
    def grade(solution):
        exercise = solution.template
        program_name = solution.file_path
        compile_command = exercise.compile_command
        compile_args = len(compile_command.split())
        run_command = exercise.run_command
        run_args = len(run_command.split())
        input_name = exercise.get_directory() + '/' + exercise.input_name
        output_name = exercise.get_directory() + '/' + exercise.output_name
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bash_command = dir_path + '/run.sh ' + solution.get_directory() + ' ' + program_name + ' ' + input_name + ' ' + output_name + ' ' + str(
            compile_args) + ' ' + str(run_args) + ' ' + compile_command + ' ' + run_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if len(output) == 0:
            solution.points = exercise.max_points
        else:
            solution.points = 0
        ExerciseService.accept_best_solution(solution.user_id, exercise)

    @staticmethod
    def exercise_query(form, id=None):
        query = db.session.query(Solutions).select_from(Solutions, User, Course, Lesson, ExerciseTemplate). \
            join(User, User.id == Solutions.user_id). \
            join(ExerciseTemplate, Solutions.exercise_template_id == ExerciseTemplate.id). \
            join(Lesson, Lesson.id == ExerciseTemplate.lesson_id). \
            join(Course, Course.id == Lesson.course_id)

        if form.status.data != SolutionStatus.ALL:
            query = query.filter(Solutions.status == form.status.data)
        if form.points_from.data is not None:
            query = query.filter(Solutions.points >= form.points_from.data)
        if form.points_to.data is not None:
            query = query.filter(Solutions.points <= form.points_to.data)
        if not len(form.course.data) == 0:
            query = query.filter(Course.name == form.course.data)
        if not len(form.lesson.data) == 0:
            query = query.filter(Lesson.name == form.lesson.data)
        # Admin is able to search by name and surname, student can only view his solutions
        from app.admin.forms import SolutionAdminSearchForm
        if isinstance(form, SolutionAdminSearchForm):
            if not len(form.surname.data) == 0:
                query = query.filter(User.surname == form.surname.data)
            if not len(form.name.data) == 0:
                query = query.filter(User.name == form.name.data)
        else:
            query = query.filter(User.id == id)
        if not len(form.exercise.data) == 0:
            query = query.filter(ExerciseTemplate.name == form.exercise.data)
        return query
