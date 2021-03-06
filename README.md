Pointer - web application for automatic grading of programming tasks (Jagiellonian University - Bachelor thesis)
----------------
The subject of this thesis is a web application for automatic grading of programming tasks, in which academic teachers can create courses, lessons and exercises. The program is evaluated by running it against the specified arguments and then comparing its results with the template output file provided by the teacher. The platform has been implemented in the Python programming language using the Flask framework and the SQLite database engine.

download project
--------------
sudo apt install git\
git clone https://github.com/michaljk1/Pointer.git

install packages
--------------
sudo apt-get install python3.8-dev\
sudo apt install python3-pip\
sudo apt install python3-venv\
sudo apt install python3-virtualenv\
sudo pip3 install python-dotenv

open project directory
-------------
cd Pointer

create venv
--------------
python3 -m venv venv
virtualenv -p python3.8 venv\
source venv/bin/activate\
(venv$) pip3 install -r requirements.txt

configure project
--------------
fill config data in config.py

install redis:
--------------
sudo apt install redis-server\
sudo apt install python3-rq

create queue for emails:
--------------
(venv)$ rq worker pointer-emails

(amount of queues is equal to amount of pointing jobs in the same time)
create queues for solutions:
--------------
(venv)$ rq worker pointer-solutions

create database
--------------
(venv)$ flask db init\
(venv)$ flask db migrate\
(venv)$ flask db upgrade

create moderator account
--------------
(venv)$ python3 create_admin.py 'admin@email.com' 'adminName' 'adminSurname' 'adminPassword'

email info
--------------
Only users with confirmed emails are able to use pointer. When application is running not at production server there is an issue with handling emails - application will be treated as not secure. For development and test purposes demanding from users having their emails confirmed can be omitted - comment lines from 65-69 in app/auth/auth_routes.py file

run application
--------------
(venv)$ flask run

backup
--------------
open copyfiles.sh and specify target dir, instance and db paths, next run\
./copyfiles.sh &

