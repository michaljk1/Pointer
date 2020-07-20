# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import bp
from app.admin.admin_forms import LessonForm, EditLessonForm
from werkzeug.utils import redirect, secure_filename
from app.models.usercourse import Course, User
from app.models.lesson import Lesson
from app import db
from app.services.ValidationUtil import validate_course, validate_lesson


@bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id: int):
    lesson: Lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_lesson(current_user, User.Roles['ADMIN'], lesson)
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
@login_required
def add_lesson(course_name: str):
    course: Course = Course.query.filter_by(name=course_name).first()
    validate_course(current_user, User.Roles['ADMIN'], course)
    form = LessonForm()
    if request.method == 'POST' and form.validate_on_submit():
        lesson_name = form.name.data
        if not course.is_lesson_name_proper(lesson_name):
            flash('Wprowadź inną nazwę lekcji', 'error')
            return redirect(url_for('admin.add_lesson', course_name=course.name))
        new_lesson = course.add_lesson(lesson_name, request.files['pdf_content'], request.form.get('editordata'))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_id=new_lesson.id))
    return render_template('admin/add_lesson.html', form=form, course=course)


@bp.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id: int):
    lesson: Lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_lesson(current_user, User.Roles['ADMIN'], lesson)
    form = EditLessonForm(text_content=lesson.content_text)
    if request.method == 'POST' and form.validate_on_submit():
        lesson.edit(request.files['pdf_content'], request.form.get('editordata'))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_id=lesson.id))
    return render_template('admin/edit_lesson.html', form=form, lesson=lesson)
