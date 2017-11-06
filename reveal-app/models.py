from wtforms import Form, StringField, PasswordField, validators, SelectField, TextAreaField
from wtforms.fields.html5 import EmailField, IntegerField


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


class ProfileForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=25)])
    surname = StringField('Surname', [validators.Length(min=1, max=25)])
    age = IntegerField('Age')
    twitter = StringField('Twitter', [validators.Length(min=1, max=25)])
    instagram = StringField('Instagram', [validators.Length(min=1, max=25)])
    city = StringField('City', [validators.Length(min=1, max=40)])
    country = StringField('Country', [validators.Length(min=1, max=25)])
    aboutMe = StringField('About Me', [validators.Length(min=1, max=140)])


class SettingsForm(Form):
    gender = SelectField(u'Gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    interested_in = SelectField(u'Interested In', choices=[('Men', 'Men'), ('Women', 'Women'), ('Both', 'Both')])
    max_distance = IntegerField('Maximum Distance (in miles)')
    age_gap = IntegerField('Age Gap (in Years)')


class ChangePasswordForm(Form):
    current_password = PasswordField('Current Password')
    new_password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=25),
        validators.EqualTo('new_password_confirm', message='Passwords do not match')
    ])
    new_password_confirm = PasswordField('Confirm Password')


class ChatBoxForm(Form):
    message = StringField('Your message: ', [validators.Length(min=1, max=140)])