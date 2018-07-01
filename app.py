from flask import Flask
from flask import render_template, url_for, jsonify, request
from flask_simplelogin import SimpleLogin, login_required, get_username
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from json import loads
from sqlalchemy import func
from flask_heroku import Heroku
from config import Config
from datetime import datetime
app = Flask(__name__)
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    heroku = Heroku(app)
except KeyError:
    app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


my_users = {
            'slava': {'password': 'slava', 'roles': []},
            'vita': {'password': 'vita', 'roles': []}
            }


class Spend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(25), default='Primary')
    category = db.Column(db.String(25))
    value = db.Column(db.Float(asdecimal=True), default=0)
    type = db.Column(db.String(10))
    short_description = db.Column(db.String(80), default=None)
    made_by = db.Column(db.String(10))
    day_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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
    try:
        last_transaction = Spend.query.all()[-1]
    except IndexError:
        last_transaction = 0

    outcome_sum = db.session.query(func.sum(Spend.value)).filter(Spend.type == 'outcome').first()[0] or 0
    income_sum = db.session.query(func.sum(Spend.value)).filter(Spend.type == 'income').first()[0] or 0
    balance = income_sum - outcome_sum
    return render_template('index.html', balance=balance, income_sum=income_sum,
                           last_transaction=last_transaction,
                           outcome_sum=outcome_sum,)


@app.route('/process', methods=['GET', 'POST'])
def process():
    fields_data = loads(request.form['fields_data'])
    print(fields_data)
    if fields_data[0] and fields_data[1]:
        spend = Spend(category=fields_data[0], value=fields_data[1],
                      type=fields_data[2], short_description=fields_data[3],
                      made_by=get_username())

        db.session.add(spend)
        db.session.commit()
        return jsonify({'val': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
