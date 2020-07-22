ensure python 3.8 is installed

download project
--------------
sudo apt install git,
git clone https://github.com/michaljk1/Pointer.git

install packages
--------------
sudo apt install python3-pip,
sudo apt install python3-venv,
sudo apt install python3-virtualenv,
sudo pip3 install python-dotenv

open project directory
-------------
cd Pointer

create venv
--------------
python3 -m venv venv,
virtualenv -p python3.8 venv,
source venv/bin/activate,
pip3 install -r requirements.txt

configure project
--------------
fill config data in config.py

create database
--------------
flask db init,
flask db migrate,
flask db upgrade,
python3 create_mod.py

install redis:
--------------
sudo apt install redis-server,
sudo apt install python3-rq

create queue for emails:
--------------
rq worker pointer-emails

(amount of queues is equal to amount of pointing jobs in the same time)
create queues for solutions:
--------------
rq worker pointer-solutions

run application
--------------
flask run

email info
--------------
for development and test purposes users with not confirmed emails are able to use pointer, uncomment 62-65 lines in app/auth/auth_routes.py file for production
