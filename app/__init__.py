from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from config import db_path
import os

app = Flask(__name__)
app.config.from_object("config")


db = SQLAlchemy(app)
Session(app)

# set up date base if it doesn't exist
if not os.path.exists(db_path):
    from app.models import User, Feed
    db.create_all()


# module level import need to be here to avoid a pesky cicular import.
from app import views
