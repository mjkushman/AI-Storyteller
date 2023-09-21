from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4

db = SQLAlchemy()



class User(db.Model):
    """Authenticated users writing the story """
     
    __tablename__ = 'users'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    # contributions = db.relationship('Contributions')


class Guest(db.Model):
    """ Holds user ids for users who have not authenticated"""

    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(
        db.UUID(as_uuid=True), 
        db.ForeignKey('users.id', ondelete='cascade'), 
        nullable=True)
    


class Story(db.Model):
    """ The context framework used to guide the story, including prompt, characters"""

    __tablename__= 'stories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.Text)
    story_prompt = db.Column(db.Text)
    objective = db.Column(db.Text) # Not Needed, remove?
    characters = db.Column(db.Text) 

    user = db.relationship('User', secondary='contributions', backref='stories')

    contributions = db.relationship('Contribution')
    # Add method to add a contribution to this story. Adding a contribution should instantiate a new Contribution 

    # methods
    def add_to_story(self,role,text,guest_id=None,user_id=None,tokens=None):
        ''' Adds a contribution to this story. '''

        contribution = Contribution(story_id=self.id, body=text, role=role, guest_id=guest_id, user_id=user_id,tokens=tokens)
        db.session.add(contribution)
        db.session.commit()

    def get_recent(self,num=4):
        ''' Return the most recent num contributions. Defaults to 4'''

        return (
            [{'role':contribution.role, 'content':contribution.body} for contribution in self.contributions[-(min(len(self.contributions), num)):]]
        )



    def serialize(self):
        ''' return a dictionary representing this story '''

        return {
            'id': self.id,
            'genre': self.genre,
            'story_prompt': self.story_prompt,
            'characters': self.characters,
            'contributions': [{
                'id': item.id,
                'body': item.body
                                } for item in self.contributions]
        }


class Contribution(db.Model):
    """ This table stores each story contribution made by a user or the AI """

    __tablename__= 'contributions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'),nullable=True)
    role = db.Column(db.Text)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id',ondelete='cascade'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    tokens = db.Column(db.Integer)
    body = db.Column(db.Text, nullable=False)



# REMOVING THIS MODEL

# class Story():
#     """ the combination of a user and context. Contains contributions from user and AI"""

#     __tablename__='stories'

#     context_id = db.Column(db.Integer, db.ForeignKey('contexts.id'), primary_key=True)
#     context = db.relationship('Context', backref='story')
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
#     contribution = db.Column(db.Text)

#     # conversation = 



# DO NOT MODIFY THIS FUNCTION
def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
