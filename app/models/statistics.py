#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List
from app.models.usercourse import Course, User
from app.models.userexercise import UserExercise


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
