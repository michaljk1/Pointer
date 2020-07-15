from flask import Flask

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from redis import Redis
import rq

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
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.default import bp as default_bp
    app.register_blueprint(default_bp)

    from app.mod import bp as mod_bp
    app.register_blueprint(mod_bp, url_prefix='/mod')

    from app.admin import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/admin')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.solution_queue = rq.Queue('pointer-solutions', connection=app.redis)
    app.email_queue = rq.Queue('pointer-emails', connection=app.redis)

    return app
