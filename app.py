from flask import Flask
from flask import render_template, url_for, jsonify
from flask_simplelogin import SimpleLogin, login_required, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from json import loads

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

basedir = os.path.abspath(os.path.dirname(__file__))

POSTGRES = {
    'user': 'wallet_user',
    'pw': 'p@ss@!worD',
    'db': 'wallet_db',
    'host': 'postgres',
    'port': '5432',
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'my_task_secret_key'

db = SQLAlchemy(app)
my_users = {'slava': {'password': 'slava', 'roles': []}}


def check_my_users(user):
    user_data = my_users.get(user['username'])
    if not user_data:
        return False
    elif user_data.get('password') == user['password']:
        return True
    return False


SimpleLogin(app, login_checker=check_my_users)


@app.route('/', methods=['GET', 'POST'])
@login_required
def hello_world():
    return render_template('index.html')


@app.route('/process', methods=['GET', 'POST'])
def process():
    fields_data = loads(request.form['fields_data'])
    return fields_data, jsonify({'val': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
