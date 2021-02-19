"""
This file contains the declarations of the models.
"""

from dataclasses import dataclass
from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@dataclass  # dataclass is used to allow for converting objects to JSON in the webservice
class User(db.Model, UserMixin):
    id: int
    username: str
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}', image_file='{self.image_file}')>"


@dataclass  # using dataclass you don't need to have the serialize function, see lec and lab 10
class Post(db.Model):
    # but you need to identify the types of the fields
    id: int
    title: str
    content: str
    content_type: str
    author: User

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship(User, backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f"<Post(id='{self.id}', title='{self.title}', date_posted='{self.date_posted}')>"

    # but with the serialize() allows you to get information from relationships
    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'content_type': self.content_type,
            'user': self.user_id,
            'username': self.user.username
        }


@dataclass
class Comment(db.Model):
    id: int
    content: str
    author: User

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship(User, backref=db.backref('comments', lazy=True))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship(Post, backref=db.backref('comments',
                                                    order_by='Comment.date_posted.desc()',
                                                    lazy=True,
                                                    # the following line enables deleting automatically
                                                    # the comments of a post when deleting the post
                                                    # uncomment to activate it
                                                    # cascade="all, delete-orphan"
                                                    ))

    def __repr__(self):
        return f"<Comment(id='{self.id}', post='{self.post_id}', user='{self.user_id}', date_posted='{self.date_posted}')>"


@dataclass
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_expired = db.Column(db.DateTime, nullable=False)
    token = db.Column(db.String(60), nullable=False, index=True, unique=True)  # index helps speeding up the searching
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('tokens', lazy=True))
