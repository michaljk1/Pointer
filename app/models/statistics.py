# -*- coding: utf-8 -*-
from typing import List

from app.models.exercise import Exercise
from app.models.usercourse import Course, User, Student


# Statistics for given course and user
# statistics for teacher includes points from exercises which haven't finished
# student should not be able to see these values
class Statistics:
    def __init__(self, course: Course, student: Student, for_teacher=False):
        if for_teacher:
            self.student_exercises, self.user_points = StudentExercise.get_student_exercises_for_teacher(student, course)
        else:
            self.student_exercises, self.user_points = StudentExercise.get_student_exercises_for_student(student, course)
        self.course_points = course.get_course_points()
        self.user_email = student.email
        self.user_index = student.index
        self.user_id = student.id
        self.course_name = course.name
        self.course_id = course.id

    def get_percent_value(self):
        if self.course_points > 0:
            return round((self.user_points / self.course_points * 100), 2)
        else:
            return float(0)

    @staticmethod
    def prepare_statistics(students: List[Student], courses: List[Course]):
        statistics_list = []
        for course in courses:
            for student in students:
                statistics_list.append(Statistics(course=course, student=student, for_teacher=True))
        return statistics_list

    # method used in export
    # generates statistics based on list of lists with course and user ids
    # format: ['[1, 3]', '[2, 3]', '[3, 3]']
    @staticmethod
    def get_statistics_by_ids(infos):
        statistics = []
        for info in infos:
            course_id, student_id = info.strip('()').strip('[]').split(',')
            course = Course.query.filter_by(id=course_id).first()
            student = Student.query.filter_by(id=student_id).first()
            statistics.append(Statistics(course, student, True))
        return statistics


class StudentExercise:
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
    def get_student_exercises_for_student(user: User, course: Course):
        user_points, student_exercises = 0.0, []
        for exercise in course.get_exercises():
            user_solution = exercise.get_user_active_solution(user_id=user.id)
            if user_solution is not None and exercise.is_finished():
                student_exercises.append(StudentExercise(exercise=exercise, points=user_solution.points))
                user_points += user_solution.points
            else:
                student_exercises.append(StudentExercise(exercise=exercise, points=0.0))
        return student_exercises, user_points

    @staticmethod
    def get_student_exercises_for_teacher(user: User, course: Course):
        user_points, student_exercises = 0.0, []
        for exercise in course.get_exercises():
            user_solution = exercise.get_user_active_solution(user_id=user.id)
            if user_solution is not None:
                student_exercises.append(StudentExercise(exercise=exercise, points=user_solution.points))
                user_points += user_solution.points
            else:
                student_exercises.append(StudentExercise(exercise=exercise, points=0.0))
        return student_exercises, user_points
