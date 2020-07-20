download project
--------------
sudo apt install git
git clone https://github.com/michaljk1/Pointer.git

install packages
--------------
sudo apt install redis-server,
sudo apt install python3-rq,
sudo apt install python3-pip,
sudo apt install python3-flask,
sudo pip3 install flask_sqlalchemy,
sudo pip3 install python-dotenv,
sudo apt-get install python3-venv

create venv
--------------
python3 -m venv venv,
virtualenv -p python3.7 venv,
source venv/bin/activate

configure project
--------------
fill your data

create database
--------------
flask db init,
flask db upgrade,
flask db migrate,
python create_mod.py

create queue for emails:
--------------
rq worker pointer-emails

(amount of queues is equal to amount of pointing jobs  in the same time)
create queues for solutions:
--------------
rq worker pointer-solutions

run application
--------------
flask run
