from flask import Flask
from flask import render_template, url_for, jsonify
from flask_simplelogin import SimpleLogin, login_required, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from json import loads
from sqlalchemy import func

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
POSTGRES = {
    'user': 'w_app_user',
    'pw': 'p@ss@!worD2',
    'db': 'app',
    'host': 'localhost',
    'port': '5432',
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'my_task_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


my_users = {'slava': {'password': 'slava', 'roles': []}}


class Spend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String, default=None)
    category = db.Column(db.String)
    value = db.Column(db.Float(precision=(5,2), asdecimal=True))

    def __repr__(self):
        return '<{} {}>'.format(self.category, self.value)


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
    balance = db.session.query(func.sum(Spend.value)).one()[0]
    return render_template('index.html', balance=balance)


@app.route('/process', methods=['GET', 'POST'])
def process():
    fields_data = loads(request.form['fields_data'])
    if fields_data[0] and fields_data[1]:
        spend = Spend(category=fields_data[0], value=fields_data[1])
        db.session.add(spend)
        db.session.commit()
        # return jsonify({'val': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
