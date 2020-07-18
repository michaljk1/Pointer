#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app.models.exercise import Exercise
from app.models.usercourse import User, Course


class UserExercise:
    def __init__(self, exercise: Exercise, points: float):
        self.exercise = exercise
        self.points = points
        self.course = exercise.get_course()
        self.lesson = exercise.lesson
        self.max_points = exercise.get_max_points()

    def get_percent_value(self):
        if self.max_points > 0:
            return round((self.points / self.max_points * 100), 2)
        else:
            return float(0)

    # includes only exercises which finished
    @staticmethod
    def get_user_exercises_for_student(user: User, course: Course):
        user_points, user_exercises = 0.0, []
        for exercise in course.get_exercises():
            user_solution = exercise.get_user_active_solution(user_id=user.id)
            if user_solution is not None and exercise.is_finished():
                user_exercises.append(UserExercise(exercise=exercise, points=user_solution.points))
                user_points += user_solution.points
            else:
                user_exercises.append(UserExercise(exercise=exercise, points=0.0))
        return user_exercises, user_points

    @staticmethod
    def get_user_exercises_for_admin(user: User, course: Course):
        user_points, user_exercises = 0.0, []
        for exercise in course.get_exercises():
            user_solution = exercise.get_user_active_solution(user_id=user.id)
            if user_solution is not None:
                user_exercises.append(UserExercise(exercise=exercise, points=user_solution.points))
                user_points += user_solution.points
            else:
                user_exercises.append(UserExercise(exercise=exercise, points=0.0))
        return user_exercises, user_points
