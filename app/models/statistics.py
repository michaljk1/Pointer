# -*- coding: utf-8 -*-
from typing import List

from app.models.exercise import Exercise
from app.models.usercourse import Course, User


# Statistics for given course and user
# statistics for admin includes points from exercises which haven't finished
# student should not be able to see these values
class Statistics:
    def __init__(self, course: Course, user: User, for_admin=False):
        if for_admin:
            self.user_exercises, self.user_points = UserExercise.get_user_exercises_for_admin(user, course)
        else:
            self.user_exercises, self.user_points = UserExercise.get_user_exercises_for_student(user, course)
        self.course_points = course.get_course_points()
        self.user_email = user.email
        self.user_index = user.index
        self.user_id = user.id
        self.course_name = course.name
        self.course_id = course.id

    def get_percent_value(self):
        if self.course_points > 0:
            return round((self.user_points / self.course_points * 100), 2)
        else:
            return float(0)

    @staticmethod
    def prepare_statistics(users: List[User], courses: List[Course]):
        statistics_list = []
        for course in courses:
            for user in users:
                statistics_list.append(Statistics(course=course, user=user, for_admin=True))
        return statistics_list

    # method used in export
    # generates statistics based on list of lists with course and user ids
    # format: ['[1, 3]', '[2, 3]', '[3, 3]']
    @staticmethod
    def get_statistics_by_ids(infos):
        statistics = []
        for info in infos:
            course_id, user_id = info.strip('()').strip('[]').split(',')
            course = Course.query.filter_by(id=course_id).first()
            user = User.query.filter_by(id=user_id).first()
            statistics.append(Statistics(course, user, True))
        return statistics


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
