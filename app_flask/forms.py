from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, email_validator
from wtforms import ValidationError

class LoginForm(FlaskForm):
    userID = StringField('userID', validators=[DataRequired()])
    userPassword = PasswordField('userPassword',validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    userID = StringField('userID', validators=[DataRequired()])
    userPassword = PasswordField('userPassword',validators=[DataRequired()])
    displayName = StringField('displayName', validators=[DataRequired()])
    submit = SubmitField('Register')
