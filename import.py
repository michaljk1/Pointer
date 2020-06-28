import os
commands = [
    "pip install flask-sqlalchemy",
    "pip install flask-migrate",
    "pip install flask-login",
    "pip install flask-wtf",
    "pip install Flask-User",
    "pip install flask-bootstrap",
    "pip install python-dotenv",
    "pip install flask-mail",
    "pip install pyjwt",
    "pip install setuptools",
    # "pip install mysqlclient",
    "pip install pytz"
#    "pip install pdfkit"
    ]
# sudo apt-get install python3-dev
for command in commands:
    os.system(command)
