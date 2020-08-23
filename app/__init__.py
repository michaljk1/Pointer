# -*- coding: utf-8 -*-
import rq
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

from config import Config

migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    from app.admin import bp as mod_bp
    app.register_blueprint(mod_bp, url_prefix='/admin')

    from app.teacher import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/teacher')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.solution_queue = rq.Queue('pointer-solutions', connection=app.redis)
    app.email_queue = rq.Queue('pointer-emails', connection=app.redis)


    return app
