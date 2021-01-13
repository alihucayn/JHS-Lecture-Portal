from flask_login import current_user
from flask_wtf import FlaskForm
from .database import User
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError

class RegistrationForm(FlaskForm):
    name=StringField("Full Name", validators=[DataRequired("Name is Required")])
    email=StringField("Email", validators=[DataRequired("Email is Required"), Email(message="Enter Email in Correct Format")])
    password=PasswordField("Password", validators=[DataRequired("Password is Required"), Length(min=8, message="Password should be atleast 8 Characters long")])
    confirm_password=PasswordField("Confirm Password", validators=[DataRequired("Confirming Password is Required"), EqualTo("password")])
    campus=SelectField("Campus", validators=[DataRequired("Selecting your Campus is Required")])
    grade=SelectField("Class", validators=[DataRequired("Selecting your Class is Required")])
    section=SelectField("Section", validators=[DataRequired("Selecting your Section is Required")])
    submit=SubmitField("Sign Up") 

    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The email is already registered with another account. Please choose another one.")

class LoginForm(FlaskForm):
    email=StringField("Email", validators=[DataRequired("Email is Required"),Email(message="Enter Email in Correct Format")])
    password=PasswordField("Password", validators=[DataRequired("Password is Required"), Length(min=8, message="Password should be atleast 8 Characters Long")])
    remember=BooleanField("Remember Me")
    submit=SubmitField("LogIn")

    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("There is no account associated with that email.")

class UpdateAccountForm(FlaskForm):
    name=StringField("Name", validators=[DataRequired()])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    campus=SelectField("Campus", validators=[DataRequired("Selecting your Campus is Required")])
    grade=SelectField("Class", validators=[DataRequired("Selecting your Class is Required")])
    section=SelectField("Section", validators=[DataRequired("Selecting your Section is Required")])
    submit = SubmitField("Update")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("That email is taken. Please choose a different one.")


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')