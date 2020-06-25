from app.models.usercourse import Course, User, role


class Statistics:
    def __init__(self, course: Course, user: User, is_admin: bool):
        if is_admin:
            self.user_points = user.get_points_admin(course)
        else:
            self.user_points = user.get_points_student(course)
        self.course_points = course.get_course_points()
        self.user_email = user.email
        self.course_name = course.name

    def get_percent_value(self):
        return round((self.user_points / self.course_points * 100), 2)
