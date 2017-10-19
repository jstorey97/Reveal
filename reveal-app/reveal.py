import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from models import RegisterForm, LoginForm, ProfileForm, SettingsForm

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

# tais.ren@fxe.us


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(25))

    registeredAt = db.Column(db.DateTime())

    confirmed = db.Column(db.Boolean())
    confirmedAt = db.Column(db.DateTime())

    currentLoginAt = db.Column(db.DateTime())

    currentLoginIP = db.Column(db.String(100))
    currentLocation = db.Column(db.String(70))
    lat = db.Column(db.Float(15))
    long = db.Column(db.Float(15))


class Profile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(65))
    firstName = db.Column(db.String(25))
    surname = db.Column(db.String(40))

    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)

    instagram = db.Column(db.String(40))
    twitter = db.Column(db.String(40))

    city = db.Column(db.String(30))
    country = db.Column(db.String(40))

    aboutMe = db.Column(db.String(140))


class Setting(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    showMe = db.Column(db.String(10))
    searchDistance = db.Column(db.Integer)

    settingsEdited = db.Column(db.Boolean())


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

        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            user = User(email=form.email.data,
                        password=sha256_crypt.encrypt(str(form.password.data)),
                        registeredAt=datetime.now(),
                        confirmed=False)
            db.session.add(user)
            db.session.commit()

            user_settings = Setting()
            db.session.add(user_settings)
            db.session.commit()

            user_profile = Profile()
            db.session.add(user_profile)
            db.session.commit()

            token = s.dumps(form.email.data)

            msg = Message('Confirm email', sender='Trump4cast@gmail.com', recipients=[form.email.data])
            link = url_for('confirmed', token=token, _external=True)
            msg.body = f"Your confirmation link is: {link}"
            mail.send(msg)

            return redirect(url_for('confirm_email'))

        else:
            flash("Email address is already being used!")

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
        user.confirmedAt = datetime.now()
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
                user = User.query.filter_by(email=email).first()

                user.currentLoginAt = datetime.now()
                user.currentLoginIP = request.remote_addr

                # We'll find the current location here later, maybe in dashboard

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

    user_settings = Setting.query.get(int(current_user.get_id()))
    user_profile = Profile.query.get(int(current_user.get_id()))

    if user_settings.settingsEdited:
        return render_template('dashboard.html',
                               fullname=user_profile.fullname,
                               edited=True,
                               )

    else:
        return render_template('dashboard.html',
                               fullname="John Smith",
                               edited=False
                               )


@app.route('/profile',  methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm(request.form)
    user = User.query.filter_by(email=load_user(current_user.get_id()).email).first()

    return render_template('profile.html',
                           form=profile_form)


@app.route('/settings',  methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(request.form)

    # Use SQL to grab persons data, update using
    # settings_form.interested_in.default = "Women"
    # settings_form.process()

    if request.method == 'POST' and form.validate():
        gender = form.gender.data
        interested_in = form.interested_in.data
        max_distance = form.max_distance.data
        age_gap = form.age_gap.data

        user = 


    return render_template('settings.html',
                           form=form)


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