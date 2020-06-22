from app import db
from app.models import Solution, User, Course, Lesson, Exercise, LoginInfo, role


def exercise_query(form, user_id=None, courses=None):
    query = db.session.query(Solution).select_from(Solution, User, Course, Lesson, Exercise). \
        join(User, User.id == Solution.user_id). \
        join(Exercise, Solution.exercise_id == Exercise.id). \
        join(Lesson, Lesson.id == Exercise.lesson_id). \
        join(Course, Course.id == Lesson.course_id)

    if form.status.data != Solution.solutionStatus['ALL']:
        query = query.filter(Solution.status == form.status.data)
    if form.points_from.data is not None:
        query = query.filter(Solution.points >= form.points_from.data)
    if form.points_to.data is not None:
        query = query.filter(Solution.points <= form.points_to.data)

    if form.course.data != 'All':
        query = query.filter(Course.name == form.course.data)
    else:
        if courses is None:
            query = query.filter(1 == 0)
        else:
            query = query.filter(Course.name.in_(courses))

    if not len(form.lesson.data) == 0:
        query = query.filter(Lesson.name == form.lesson.data)
    # Admin is able to search by name and surname, student can only view his solutions
    from app.admin.forms import SolutionAdminSearchForm
    if isinstance(form, SolutionAdminSearchForm):
        if form.surname.data is not None and len(form.surname.data) > 0:
            query = query.filter(User.surname == form.surname.data)
        if form.name.data is not None and len(form.name.data) > 0:
            query = query.filter(User.name == form.name.data)
    else:
        query = query.filter(User.id == user_id)
    if not len(form.exercise.data) == 0:
        query = query.filter(Exercise.name == form.exercise.data)
    return query


def login_query(form, user_role, ids=None):
    query = db.session.query(LoginInfo).select_from(LoginInfo).join(User, User.id == LoginInfo.user_id)
    if form.status.data != LoginInfo.loginStatus['ALL']:
        query = query.filter(LoginInfo.status == form.status.data)

    if form.ip_address.data != '':
        query = query.filter(LoginInfo.ip_address == form.ip_address.data)
    if form.email.data != 'All':
        query = query.filter(User.email == form.email.data)
    elif user_role == role['MODERATOR']:
        query = query.filter(User.role == role['ADMIN'])
    elif user_role == role['ADMIN']:
        if ids is None or len(ids) == 0:
            query = query.filter(1 == 0)
        else:
            query = query.filter(User.id.in_(ids))
    return query
