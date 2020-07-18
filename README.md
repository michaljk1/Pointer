apt-get install python3-venv
python3 -m venv venv
virtualenv -p python3.7 venv
source venv/bin/activate
pip install flask
pip install -r requirements.txt