import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from models import RegisterForm, ConfirmationForm, LoginForm

from datetime import datetime
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config.from_pyfile("email_conf.py")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.getcwd())+"\database.db"
app.secret_key = 'BULKpowders2017'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mail = Mail(app)
s = URLSafeTimedSerializer('ThisIsASecret')

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(25))
    surname = db.Column(db.String(40))
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(25))

    confirmed = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())

    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))

    registered_at = db.Column(db.DateTime())


class Settings(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(40), unique=True)

    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)

    instagram = db.Column(db.String(40))
    twitter = db.Column(db.String(40))

    show_me = db.Column(db.String(10))
    max_range = db.Column(db.Integer)

    settings_edited = db.Column(db.Boolean())


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
        user = User(first_name=form.name.data.split()[0],
                    surname=' '.join(form.name.data.split()[1:]),
                    email=form.email.data,
                    password=sha256_crypt.encrypt(str(form.password.data)),
                    registered_at=datetime.now(),
                    current_login_ip=request.remote_addr,
                    confirmed=False)

        db.session.add(user)
        db.session.commit()

        user_settings = Settings(email=form.email.data,
                                 settings_edited=False)

        db.session.add(user_settings)
        db.session.commit()

        token = s.dumps(form.email.data)

        msg = Message('Confirm email', sender='Trump4cast@gmail.com', recipients=[form.email.data])
        link = url_for('confirmed', token=token, _external=True)
        msg.body = f"Your confirmation link is: {link}"
        mail.send(msg)

        return redirect(url_for('confirm_email'))

    return render_template('register.html',
                           form=form)


@app.route('/register/confirm/')
def confirm_email():
    return render_template('email_confirmation.html')


@app.route('/register/confirmed?<token>')
def confirmed(token):
    try:
        email = s.loads(token, max_age=6000)

        user = User.query.filter_by(email=email).first()
        user.confirmed = True
        user.confirmed_at = datetime.now()
        db.session.commit()

        return render_template('email_confirmed.html')

    except SignatureExpired:
        # Have something here to deal with this later
        pass


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.email.data

        user = User.query.filter_by(email=email).first()

        if user is not None and sha256_crypt.verify(password, user.password):
            if not user.confirmed:
                flash("Please confirm your email before logging in!")

            else:
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))

        else:
            flash("Incorrect email or the address is not registered")

    return render_template('login.html',
                           form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = load_user(current_user.get_id())

    fullname = f'{user.first_name} {user.surname}'
    user_settings = Settings.query.filter_by(email=user.email).first()

    if user_settings.settings_edited:
        return render_template('dashboard.html',
                               fullname=fullname,
                               edited=True,
                               )

    else:
        return render_template('dashboard.html',
                               fullname=fullname,
                               edited=False,
                               )
1


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for(index))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)