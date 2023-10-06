from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()



class User(db.Model):
    """Authenticated users writing the story """
     
    __tablename__ = 'users'

    def __repr__(self):
        s = self
        return f'User id: {s.id}, created_at: {s.created_at}, first_name: {s.first_name}, username:{s.username}, (rel backlink) stories: {s.stories}'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    username = db.Column(db.String(50))

    # stories = db.relationship('Story')
    # contributions = db.relationship('Contributions')

    @classmethod
    def signup(cls, first_name, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
        )

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, email, password):
        """Find user with `username` and `password`.
        If can't find matching user (or if password is wrong), returns False.

        I took this method from the Warbler project.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False



# class Guest(db.Model):
#     """ Holds user ids for users who have not authenticated"""

#     __tablename__ = 'guests'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow())
#     user_id = db.Column(
#         db.UUID(as_uuid=True), 
#         db.ForeignKey('users.id', ondelete='cascade'), 
#         nullable=True)



class Story(db.Model):
    """ The context framework used to guide the story, including prompt, characters"""

    __tablename__= 'stories'

    def __repr__(self):
        s = self
        return f'Story id: {s.id}, genre: {s.genre}, story_prompt: {s.story_prompt}, (rel) user:{s.user}, (rel) contributions: {s.contributions}'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.Text)
    story_prompt = db.Column(db.Text)
    objective = db.Column(db.Text) # Not Needed, remove?
    characters = db.Column(db.Text) 

    user = db.relationship('User', secondary='contributions', backref='stories')

    contributions = db.relationship('Contribution')
    # Add method to add a contribution to this story. Adding a contribution should instantiate a new Contribution 

    # methods
    def contribute(self,role,content,user_id=None,tokens=None):
        ''' Adds a contribution to this story. '''

        contribution = Contribution(story_id=self.id, content=content, role=role, user_id=user_id,tokens=tokens)
        db.session.add(contribution)
        return contribution
        # db.session.commit()

    def get_recent(self,num=7):
        ''' Return the most recent num contributions. Defaults to 4'''

        return (
            [{'role':contribution.role, 'content':contribution.content} for contribution in self.contributions[-(min(len(self.contributions), num)):]]
        )



    def serialize(self):
        ''' return a dictionary representing this story '''
        print('INSIDE THE STORY SERIALIZE')
        print('contributions:')
        print(self.contributions)
        print([c.content for c in self.contributions])
        print([ {'role':c.role, 'content':c.content} for c in self.contributions ])
        return {
            'context':{
                'id': self.id,
                'genre': self.genre,
                'story_prompt': self.story_prompt,
                'characters': self.characters
            },           
            #I'm not sure if this version of serialization will work.
            'contributions': 
            [ {'role':c.role, 'content':c.content} for c in self.contributions ]
            # [ {item.key:item.value} for item in self.contributions ]
        }


class Contribution(db.Model):
    """ This table stores each story contribution made by a user or the AI """

    __tablename__= 'contributions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    role = db.Column(db.Text)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id',ondelete='cascade'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    tokens = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False)

    def serialize(self):
        ''' Return a jsonable dictionary representing this contribution '''
        return {
            'id': self.id,
            'user_id': self.user_id
            'role': self.role,
            'story_id': self.story_id,
            'tokens': self.tokens,
            'content': self.content
        }


class AnonStory():

    ''' This model maintains a story before a user authenticates and before a story gets saved in the db'''
    
    def __init__(self,id=None,genre='',story_prompt='',characters=[],objective='',contributions=[]):
        self.id = id
        self.genre = genre
        self.story_prompt = story_prompt
        self.characters = characters
        self.objective = objective
        self.contributions = contributions

    def contribute(self,role,content,tokens=0):
        '''Accepts a role and content, then appends it to contributions list. Expects role to be "user" or "assistant" and content should be a string.'''

        self.contributions.append({'role': role,'content': content})


    def get_recent(self,num=7):
        ''' Return the most recent num contributions. Defaults to 4'''

        return (
            [{'role':contribution['role'], 'content':contribution['content']} for contribution in self.contributions[-(min(len(self.contributions), num)):]]
        )
    

    def convert_to_story(self,user):
        # todo
        print('===INSIDE CONVERT TO STORY===')
        if self.id:
            return db.session.get(Story,self.id)
        else:
            story = Story(
                genre=self.genre,
                story_prompt=self.story_prompt,
                characters=self.characters,
                objective=self.objective,
                )
            db.session.add(story)
            db.session.commit()
            for c in self.contributions:
                story.contribute(
                    user_id=(user.id if c['role'] == 'user' else None),
                    role=c['role'],
                    content = c['content'],
                    tokens=c.get('tokens')
                )
            db.session.commit()
            return story


    def serialize(self):
        return {
            'context': {
                'genre': self.genre,
                'story_prompt': self.story_prompt,
                'characters': self.characters,
                'objective': self.objective
                },
            'contributions': self.contributions
            # [ {role:text for role,text in item.items()} for item in self.contributions ]
            # [ {k: v for k, v in item} for item in self.contributions ]
        }






# DO NOT MODIFY THIS FUNCTION
def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)
