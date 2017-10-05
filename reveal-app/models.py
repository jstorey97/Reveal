from wtforms import Form, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField


class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=60)])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=25),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


class ConfirmationForm(Form):
    code = StringField('', [validators.Length(min=1, max=10)])


class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password')