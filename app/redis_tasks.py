#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import jwt
from rq import get_current_job
from flask import render_template
from app import mail
from flask_mail import Message
from flask import current_app
from time import time
from app import create_app, db
from app.models.task import Task
from app.services.SolutionUtil import execute_solution

app = create_app()
app.app_context().push()


def point_solution(solution_id):
    try:
        _set_task_progress(0)
        execute_solution(solution_id)
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)


def send_confirm_email(email):
    try:
        _set_task_progress(0)
        token = get_confirm_email_token(email)
        mail.send(Message(subject='[Pointer] Potwierdź email',
                          sender=current_app.config['ADMINS'][0],
                          recipients=[email],
                          html=render_template('email/confirm_email_request.html', token=token)))
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)


def send_course_email(email, course_name, role):
    try:
        _set_task_progress(0)
        mail.send(Message(subject='[Pointer] Nowy kurs',
                          sender=app.config['ADMINS'][0],
                          recipients=[email],
                          html=render_template('email/confirm_course.html', role=role, course_name=course_name)))
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)


def send_reset_password(email):
    try:
        _set_task_progress(0)
        token = get_reset_password_token(email)
        mail.send(Message(subject='[Pointer] Reset hasła',
                          sender=current_app.config['ADMINS'][0],
                          recipients=[email],
                          html=render_template('email/reset_password.html', token=token)))
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)


def get_confirm_email_token(email, expires_in=600):
    return jwt.encode(
        {'confirm_email': email, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


def get_reset_password_token(email, expires_in=600):
    return jwt.encode(
        {'reset_password': email, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
        db.session.commit()
