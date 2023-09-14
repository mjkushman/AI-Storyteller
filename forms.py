from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField, IntegerField, SelectField, TextAreaField
from wtforms.validators import InputRequired, NumberRange, Optional, URL


class StoryForm(FlaskForm):
    contribution = TextAreaField("", validators=[InputRequired(message='How will you add to the story?')])