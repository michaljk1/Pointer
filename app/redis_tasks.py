# -*- coding: utf-8 -*-
import sys
from time import time

import jwt
from flask import current_app
from flask import render_template
from flask_mail import Message
from rq import get_current_job

from app import create_app, db
from app import mail
from app.models.task import Task
from app.services.SolutionUtil import execute_solution

app = create_app()
app.app_context().push()


def point_solution(solution_id):
    try:
        execute_solution(solution_id)
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        set_task_complete()


def send_confirm_email(email):
    try:
        token = get_confirm_email_token(email)
        mail.send(Message(subject='[Pointer] Potwierdź email',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[email],
                          html=render_template('email/confirm_email_request.html', token=token)))
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        set_task_complete()


def send_course_email(email, course_name, role):
    try:
        mail.send(Message(subject='[Pointer] Nowy kurs',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email],
                          html=render_template('email/confirm_course.html', role=role, course_name=course_name)))
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        set_task_complete()


def send_reset_password(email):
    try:
        token = get_reset_password_token(email)
        mail.send(Message(subject='[Pointer] Reset hasła',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[email],
                          html=render_template('email/reset_password.html', token=token)))
        db.session.commit()
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        set_task_complete()


def get_confirm_email_token(email):
    return jwt.encode(
        {'confirm_email': email, 'exp': time() + current_app.config['TOKEN_EXPIRES_IN']},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


def get_reset_password_token(email):
    return jwt.encode(
        {'reset_password': email, 'exp': time() + current_app.config['TOKEN_EXPIRES_IN']},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


def set_task_complete():
    job = get_current_job()
    if job:
        task = Task.query.get(job.get_id())
        task.complete = True
        db.session.commit()
