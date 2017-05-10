from app import db
from passlib.apps import custom_app_context as pwd_context
import datetime


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    hash = db.Column(db.String(120))
    created_at = db.Column(db.DateTime())
    last_seen = db.Column(db.DateTime())

    def __init__(self, username, password):
        self.username = username.lower()
        self.hash = pwd_context.hash(password)
        self.created_at = datetime.datetime.utcnow()
        self.last_seen = datetime.datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.username


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    feed_url = db.Column(db.String(200))

    def __init__(self, feed_name, feed_url, user_id):
        self.feed_name = feed_name
        self.feed_url = feed_url
        self.user_id = user_id

    def __repr__(self):
        return '<Feed %r>' % self.feed_name
