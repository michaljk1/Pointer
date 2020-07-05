import json
from typing import List

from pointer.models.solution import Solution
from pointer.models.usercourse import Course, User, role


class Statistics:
    def __init__(self, course: Course, user: User, is_admin: bool):
        if is_admin:
            self.solutions, self.user_points = user.get_solutions_with_points_for_admin(course)
        else:
            self.solutions, self.user_points = user.get_solutions_with_points_for_student(course)
        self.course_points = course.get_course_points()
        self.user_email = user.email
        self.course_name = course.name

    def get_percent_value(self):
        if self.course_points > 0:
            return round((self.user_points / self.course_points * 100), 2)
        else:
            return float(0)
