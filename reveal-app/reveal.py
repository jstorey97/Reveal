from flask import Flask
from random import choice
from string import ascii_letters
from flask import render_template, request, redirect, url_for
from wtforms import Form, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField

app = Flask(__name__)
app.secret_key = 'BULKpowders2017'


@app.route('/')
def index():
    return render_template('index.html')


class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=50)])
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
        name = form.name.data
        email = form.email.data
        password = form.password.data
        verification_num = ''.join([choice(ascii_letters) for i in range(7)])

        print(name, email, password, verification_num)
        # Input them into SQL


        redirect(url_for('index'))

    return render_template('register.html',
                           form=form)


if __name__ == "__main__":
  app.run(debug=True)
