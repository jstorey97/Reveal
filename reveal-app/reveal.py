import os

from flask import Flask
from random import choice
from string import ascii_letters

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask import render_template, request, redirect, url_for, flash
from wtforms import Form, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from datetime import datetime

from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.getcwd())+"\database.db"
app.secret_key = 'BULKpowders2017'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(60))
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(100))

    verification_phrase = db.Column(db.String(20))
    confirmed = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())

    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))

    registered_at = db.Column(db.DateTime())


class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=60)])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        fullname = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        verification_phrase = ''.join([choice(ascii_letters) for i in range(11)])
        current_ip = request.remote_addr

        user = User(fullname=fullname, email=email, password=password,
                    verification_phrase=verification_phrase, registered_at=datetime.now(),
                    current_login_ip=current_ip)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('confirm_email',
                                name=fullname,
                                email=email))

    return render_template('register.html',
                           form=form)


class Confirmation(Form):
    code = StringField('Confirmation code', [validators.Length(min=1, max=10)])


@app.route('/register/confirm')
def confirm_email():
    form = Confirmation(request.form)
    return render_template('email_confirmation.html',
                           form=form)


class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.email.data

        user = User.query.filter_by(email=email).first()

        if user is not None and sha256_crypt.verify(password, user.password):
            login_user(user)

        else:
            flash("Incorrect email or the address is not registered")

    return render_template('login.html',
                           form=form)


if __name__ == "__main__":
  app.run(debug=True)
