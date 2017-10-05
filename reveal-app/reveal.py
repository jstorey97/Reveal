import os

from flask import Flask
from random import choice
from string import ascii_letters

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, login_required
from flask import render_template, request, redirect, url_for, flash


from models import RegisterForm, ConfirmationForm, LoginForm

from datetime import datetime
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.getcwd())+"\database.db"
app.secret_key = 'BULKpowders2017'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User(fullname=form.name.data,
                    email=form.email.data,
                    password=sha256_crypt.encrypt(str(form.password.data)),
                    verification_phrase=''.join([choice(ascii_letters) for _ in range(11)]),
                    registered_at=datetime.now(),
                    current_login_ip=request.remote_addr,
                    confirmed=False)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('confirm_email',
                                name=form.name.data,
                                email=form.email.data))

    return render_template('register.html',
                           form=form)


@app.route('/register/confirm',  methods=['GET', 'POST'])
def confirm_email():
    form = ConfirmationForm(request.form)
    return render_template('email_confirmation.html',
                           form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.email.data

        user = User.query.filter_by(email=email).first()

        if user is not None and sha256_crypt.verify(password, user.password):
            if not user.confirmed:
                flash("Please confirm your email")

            else:
                login_user(user, remember=form.remember)

        else:
            flash("Incorrect email or the address is not registered")

    return render_template('login.html',
                           form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
  app.run(debug=True)
