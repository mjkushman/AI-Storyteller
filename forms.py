from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField, IntegerField, SelectField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, NumberRange, Optional, URL, Length




class ContextForm(FlaskForm):
    genre = SelectField("Genre", validators=[InputRequired()])
    story_prompt = TextAreaField("Story Prompt", validators=[InputRequired(message='Please include a starter prompt')], id='storyPrompt', )


class StoryForm(FlaskForm):
    body = TextAreaField("", validators=[InputRequired(message='How will you add to the story?'), Length(min=1,max=100)], id='inputField')
    story_id = HiddenField("", validators=[InputRequired()])

