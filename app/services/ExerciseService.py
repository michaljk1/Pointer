import os
import subprocess

from app import db
from app.models import UserExercises


class ExerciseService:
    @staticmethod
    def accept_best_solution(user_id, exercise):
        user_exercises = UserExercises.query.filter_by(user_id=user_id, exercise_template_id=exercise.id).all()
        points = 0
        best_solution = None
        for user_exercise in user_exercises:
            if user_exercise.points >= points:
                best_solution = user_exercise
                points = best_solution.points
        best_solution.is_approved = True
        user_exercises.remove(best_solution)
        for user_exercise in user_exercises:
            user_exercise.is_approved = False
        db.session.commit()

    @staticmethod
    def grade(solution):
        exercise = solution.template
        program_name = solution.file_path
        compile_command = exercise.compile_command
        compile_args = len(compile_command.split())
        run_command = exercise.run_command
        run_args = len(run_command.split())
        input_name = exercise.get_directory()+'/'+exercise.input_name
        output_name = exercise.get_directory()+'/'+exercise.output_name
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bash_command = dir_path + '/run.sh ' + solution.get_directory() + ' ' + program_name + ' ' + input_name + ' ' + output_name + ' ' + str(compile_args) + ' ' + str(run_args) + ' ' + compile_command + ' ' + run_command
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if len(output) == 0:
            solution.points = exercise.max_points
        else:
            solution.points = 0
        ExerciseService.accept_best_solution(solution.user_id, exercise)
