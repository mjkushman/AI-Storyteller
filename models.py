from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User():
    """The user writing the story """
     
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at=db.Column(db.DateTime, default=datetime.utcnow())


class Context():
    """ The context used to guide the story, including prompt, characters, and objective"""

    __tablename__= 'contexts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.Text)
    prompt = db.Column(db.Text)
    objective = db.Column(db.Text)
    characters = db.Column(db.Text)



class Story():
    """ the combination of a user and context. Contains contributions from user and AI"""

    __tablename__='stories'

    context_id = db.Column(db.Integer, db.ForeignKey('contexts.id'), primary_key=True)
    context = db.relationship('Context', backref='story')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    contribution = db.Column(db.Text)

    # conversation = 

