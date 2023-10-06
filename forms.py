from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField, PasswordField, SelectField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, NumberRange, Optional, URL, Length, Email, EqualTo




class ContextForm(FlaskForm):
    genre = SelectField("Genre", validators=[InputRequired()])
    story_prompt = TextAreaField("Story Prompt", validators=[InputRequired(message='Please include a starter prompt')], id='storyPrompt', )

class StoryForm(FlaskForm):
    body = TextAreaField("", validators=[InputRequired(message='How will you add to the story?'), Length(min=1,max=100)], id='inputField')
    story_id = HiddenField("", validators=[InputRequired()])
    story_genre = HiddenField("")
    story_prompt = HiddenField("")

class SignUpForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(message='Please enter a name')], render_kw={"placeholder": "First Name"})
    email = StringField("Email", validators=[InputRequired(message='Email is required'), Email(message='Please enter a valid email address.')], id='email', render_kw={"placeholder": "Email"})
    username = StringField('Username', validators=[InputRequired(), Length(max=50)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')], render_kw={"placeholder": "Password"})
    confirm  = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm Password"})

class SignInForm(FlaskForm):
     email = StringField("Email", validators=[InputRequired(message='Email is required'), Email(message='Please enter a valid email address.')], id='email', render_kw={"placeholder": "Email"})
     password = PasswordField('Password', [InputRequired()], render_kw={"placeholder": "Password"})