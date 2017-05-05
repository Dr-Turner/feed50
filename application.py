from flask import Flask, render_template, url_for, session, request, flash, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime

# from helpers import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # to disable annoying warnings
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super secret'

db = SQLAlchemy(app)
Session(app)


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
        password = request.form.get("password")
        user = User(username, password)
        db.session.add(user)
        db.session.commit()

        flash("Sucessfully registered. Please log in.", "success")
        return redirect(url_for('index'))

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    # clear current user id
    if "user_id" in session:
        session.clear()

    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            flash("Username field cannot be blank", "error")
            return redirect(url_for("login"))

        # ensure password was submitted
        elif not request.form.get("password"):
            flash("Password field cannot be blank", "error")
            return redirect(url_for("login"))

        # query database for username
        username = request.form.get("username").lower()
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        # ensure username exists and password is correct
        if not user or not pwd_context.verify(password, user.hash):
            print(pwd_context.encrypt(password))
            print(user.hash)
            flash("Invalid username and/or password provided", "error")
            return redirect(url_for("login"))

        # remember which user has logged in
        session["user_id"] = user.id
        session["username"] = user.username

        # adjust user.last_seen
        user.last_seen = datetime.datetime.utcnow()
        db.session.add(user)
        db.session.commit()

        # redirect user to home page
        flash("Welcome back {}".format(user.username))
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route('/logout')
def logout():
    # clear user in session
    session.clear()

    flash("You have been logged out successfully.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
