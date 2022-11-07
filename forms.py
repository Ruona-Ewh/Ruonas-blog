from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField 
from wtforms.validators import DataRequired, Length, Email, EqualTo

class SignupForm(FlaskForm):
    firstname = StringField('First Name',  validators=[DataRequired(), Length(min=1, max=25)])
    lastname = StringField('Last Name',  validators=[DataRequired(), Length(min=1, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email(message='Inavlid Email')]) 
    password = PasswordField('Password', validators=[DataRequired()])
    confirm= PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
        
        


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    article = TextAreaField('Article', validators=[DataRequired()])