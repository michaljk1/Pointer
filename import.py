import os

commands = [
    "pip3 install flask-sqlalchemy",
    "pip3 install flask-migrate",
    "pip3 install flask-login",
    "pip3 install flask-wtf",
    "pip3 install Flask-User",
    "pip3 install flask-bootstrap",
    "pip3 install python-dotenv",
    "pip3 install flask-mail",
    "pip3 install pyjwt",
    "pip3 install setuptools",
    "pip3 install mysqlclient",
    "pip3 install pytz"
    ]
# sudo apt-get install python3-dev
for command in commands:
    os.system(command)
