from flask import Flask, render_template, url_for, Session, request, flash, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime

from helpers import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # to disable annoying warnings
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super secret'

session = Session()
session.init_app(app)

db = SQLAlchemy(app)

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

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # check username field is populated
        if not request.form.get("username"):
            flash("Username required!", "error")
            return redirect(url_for("register"))

        # check username is available
        username = request.form.get("username").lower()
        exists = User.query.filter_by(username=username).count()

        if exists:
            flash("Username already exists, please pick a different one", "error")
            return redirect(url_for("register"))

        # check password fields are populated
        if not request.form.get("password"):
            flash("Password required!", "error")
            return redirect(url_for("register"))

        # check password fields match.
        if not request.form.get("password") == request.form.get("password-repeat"):
            flash("Passwords don't match!", "error")
            return redirect(url_for("register"))

        # add user to database
        hash = pwd_context.hash(request.form.get("password"))
        user = User(username, hash)
        db.session.add(user)
        db.session.commit()

        flash("Sucessfully registered. Please log in.", "success")
        return redirect(url_for('index'))

    return render_template("register.html")


if __name__ == '__main__':
    app.run()
