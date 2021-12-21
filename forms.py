from wtforms import Form, StringField, validators, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, IntegerField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')

class SendMoneyForm(Form):
    amount = DecimalField('Amount', [validators.NumberRange(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])

class BuyForm(Form):
    amount = StringField('Amount', [validators.NumberRange(min=1, max=50)])
