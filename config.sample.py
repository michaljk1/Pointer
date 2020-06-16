import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'mysql://name:password@host/databasename'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-Mail SMTP server settings
    # Flask-User settings
    # USER_APP_NAME = "Pointer"      # Shown in and email templates and page footers
    # USER_ENABLE_EMAIL = True        # Enable email authentication
    # USER_ENABLE_USERNAME = False    # Disable username authentication
    # USER_EMAIL_SENDER_NAME = USER_APP_NAME
    # USER_EMAIL_SENDER_EMAIL = "noreply@example.com"