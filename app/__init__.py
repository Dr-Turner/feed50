from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)
Session(app)

# module level import need to be here to avoid a pesky cicular import.
from app import views
