from typing import List

from app.mod.forms import LoginInfoForm
from app.models import Course, role


def get_filled_form_with_ids(courses: List[Course]):
    user_ids = []
    form = LoginInfoForm()
    for course in courses:
        for member in course.members:
            if member.role == role['STUDENT'] and member.id not in user_ids:
                user_ids.append(member.id)
                form.email.choices.append((member.email, member.email))
    return user_ids, form
