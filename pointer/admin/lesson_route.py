import os
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from pointer.admin import bp
from pointer.admin.forms import LessonForm, EditLessonForm
from werkzeug.utils import redirect, secure_filename
from pointer.models.usercourse import Course, role
from pointer.models.lesson import Lesson
from pointer import db
from pointer.services.RouteService import validate_role_course


@bp.route('/lesson/<string:lesson_name>/')
@login_required
def view_lesson(lesson_name):
    lesson = Lesson.query.filter_by(name=lesson_name).first()
    validate_role_course(current_user, role['ADMIN'], lesson.course)
    return render_template('admin/lesson.html', lesson=lesson, course=lesson.course)


@bp.route('/<string:course_name>/add_lesson', methods=['GET', 'POST'])
@login_required
def add_lesson(course_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_role_course(current_user, role['ADMIN'], course)
    form = LessonForm()
    if request.method == 'POST' and form.validate_on_submit():
        lesson_name = form.name.data
        if not course.is_lesson_name_proper(lesson_name):
            flash('Wprowadź inną nazwę lekcji', 'error')
            return redirect(url_for('admin.add_lesson', course_name=course.name))
        file = request.files['pdf_content']
        filename = secure_filename(file.filename)
        if filename == '':
            filename = None
        new_lesson = Lesson(name=lesson_name, content_pdf_path=filename,raw_text=form.text_content.data)
        course.lessons.append(new_lesson)
        lesson_directory = new_lesson.get_directory()
        os.makedirs(lesson_directory)
        if filename is not None:
            file.save(os.path.join(lesson_directory, filename))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_name=new_lesson.name))
    return render_template('admin/add_lesson.html', form=form, course=course)


@bp.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    lesson: Lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_role_course(current_user, role['ADMIN'], lesson.course)
    form = EditLessonForm(text_content=lesson.raw_text)
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['pdf_content']
        filename = secure_filename(file.filename)
        lesson.raw_text = form.text_content.data
        if filename != '':
            lesson_dir = lesson.get_directory()
            os.remove(os.path.join(lesson_dir, lesson.content_pdf_path))
            lesson.content_pdf_path = filename
            file.save(os.path.join(lesson_dir, filename))
        db.session.commit()
        return redirect(url_for('admin.view_lesson', lesson_name=lesson.name))
    return render_template('admin/edit_lesson.html', form=form, lesson=lesson)
