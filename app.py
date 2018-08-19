from flask import Flask, send_from_directory
from flask import render_template, jsonify, request, redirect, flash, url_for
from flask_login import UserMixin, LoginManager,login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from json import loads
from sqlalchemy import func
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource
import pandas as pd
import sys, os


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db_dir/test.db' 
#os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


class Spend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(25), default='Primary')
    category = db.Column(db.String(25))
    value = db.Column(db.Float(asdecimal=True), default=0)
    type = db.Column(db.String(10))
    short_description = db.Column(db.String(80), default=None)
    made_by = db.Column(db.String(10))
    day_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<{} {}>'.format(self.category, self.value)


class AppUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SpendApi(Resource):
    def get(self):
        q = db.session.execute('select * from spend')
        data = [dict(i.items()) for i in q.fetchall()]
        return jsonify({'data': data})


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


@login.user_loader
def load_user(id):
    return AppUser.query.get(int(id))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = AppUser.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/dwld/test.db', methods=['GET', 'POST'])
def download():
    uploads = os.path.join(os.getcwd(), '..', 'db_dir')
    return send_from_directory(directory=uploads, filename='test.db')


@app.route('/stat')
def stat():
    query = db.session.execute('SELECT category, type, SUM(value) as total FROM spend GROUP BY 1,2 ORDER BY 2 DESC ')
    data = list(query)
    df = pd.DataFrame(data, columns=["category", "type", "value"])
    df_out = df.loc[df['type'] == 'outcome']
    df_in = df.loc[df['type'] == 'income']
    return render_template('stat.html', df_in=df_in, df_out=df_out)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
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
@login_required
def process():
    fields_data = loads(request.form['fields_data'])
    print(fields_data)
    if fields_data[0] and fields_data[1]:
        spend = Spend(category=fields_data[0], value=fields_data[1],
                      type=fields_data[2], short_description=fields_data[3],
                      made_by=current_user.username)

        db.session.add(spend)
        db.session.commit()
        return jsonify({'val': True})


api.add_resource(SpendApi, '/api_v1/all_transactions')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=sys.argv[1])
