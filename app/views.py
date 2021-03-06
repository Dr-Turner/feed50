import datetime
from flask import session, redirect, url_for, request, flash, render_template

from passlib.apps import custom_app_context as pwd_context

from app import db, app
from app.models import User, Feed
from app.helpers import login_required, get_rss_title, is_rss_page, get_feed


@app.route('/')
@app.route('/index')
def index():
    """A very simple welcome page"""
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # check username field is populated
        if not request.form.get("username"):
            flash("Username required!", "error")
            return redirect(url_for("register"))

        # check username is available
        username = request.form.get("username")
        # (need do use ilike to keep user model case insensitive)
        exists = User.query.filter(User.username.ilike(username)).count()

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
    if session.get("user_id"):
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

        user = User.query.filter(User.username.ilike(username)).first()

        # ensure username exists and password is correct
        if not user or not pwd_context.verify(password, user.hash):
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
        return redirect(url_for("feeds"))

    return render_template("login.html")


@app.route('/logout')
def logout():
    # clear user in session
    session.clear()

    flash("You have been logged out successfully.", "success")
    return redirect(url_for('index'))


@app.route('/feeds')
@login_required
def feeds():
    """page to display feed currently subscribed to"""
    user_feeds = Feed.query.filter_by(user_id=session["user_id"])
    return render_template('feeds.html', feeds=user_feeds)


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    """Page to enable a user to add a field to his/her profile"""
    if request.method == "POST":

        # check url field is populated
        if not request.form.get("feed_url"):
            flash("Field cannot be left blank", "error")
            return redirect(url_for("add"))

        # check url field is not more than 200 chars
        if len(request.form.get("feed_url")) > 200:
            flash("Sorry, we cannot add urls longer than 200 characters in length", "error")
            return redirect(url_for("add"))

        # check url field is actually a legit rss.
        if not is_rss_page(request.form.get("feed_url")):
            flash("Sorry, this doesn't seem to be a rss page!", "error")
            return redirect(url_for("add"))

        # get feeds title
        url = request.form.get("feed_url")
        feed_name = get_rss_title(url)

        # see if feed already exists.
        f = Feed.query.filter_by(feed_url=url, user_id=session['user_id']).count()
        if f > 0:
            flash("You are already subscribed to this feed.", "error")
            return redirect(url_for("add"))

        f = Feed(feed_name, url, session["user_id"])
        db.session.add(f)
        db.session.commit()

        flash("Rss feed added successfully", "success")
        return redirect(url_for("feeds"))

    return render_template("add.html")


@app.route('/rename/', methods=["GET", "POST"])
@app.route('/rename/<int:feed_id>', methods=["GET", "POST"])
def rename(feed_id=None):
    """allows users to rename the titles of their own feeds."""
    if request.method == "POST":
        # check feed is populated
        if not request.form.get("new_name"):
            flash("Field cannot be blank.", "error")
            return redirect(url_for("rename"))

        # check field is not in excess of 80 chars.
        if len(request.form.get("new_name")) > 80:
            flash("Sorry! feed names cannot be in excess of 80 characters", "error")
            return redirect(url_for("rename"))

        f = Feed.query.filter_by(id=session["feed_id"]).first()
        f.feed_name = request.form.get("new_name")
        db.session.commit()

        flash("Feed renamed!", "success")
        return redirect(url_for("feeds"))

    f = Feed.query.filter_by(id=feed_id).first()

    # check feed exists.
    if f is None:
        flash("Sorry, this feed does not exist", "error")
        return redirect(url_for("feeds"))

    # Check user is the correct one.
    if not f.user_id == session["user_id"]:
        flash("Sorry, you are not authorised to rename this feed.", "error")
        return redirect(url_for("feeds"))

    # store feed_id in session so it won't be lost between the get and post requests
    session["feed_id"] = feed_id

    old_name = f.feed_name
    return render_template("rename.html", old_name=old_name)  # could send old name to this


@app.route('/remove/<int:feed_id>')
@login_required
def remove(feed_id):
    """allows users to delete their own feeds."""
    query = Feed.query.filter_by(id=feed_id)

    f = query.first()
    # check feed exists.
    if f is None:
        flash("Sorry, this feed does not exist", "error")
        return redirect(url_for("feeds"))

    # Check user is the correct one.
    if not f.user_id == session["user_id"]:
        flash("Sorry, you are not autorised to delete this feed.", "error")
        return redirect(url_for("feeds"))

    """remove post from database and hence users feed list"""
    query.delete()
    db.session.commit()

    flash("Feed removed", "success")
    return redirect(url_for("feeds"))


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    """User page route. Allowing the user a dashboard of sorts."""

    # check user is user. (No implementation at this time for viewing anohter users profile)
    if not user_id == session["user_id"]:
        flash("Sorry, you can't view another user's profile", "error")
        return redirect(url_for("index"))

    u = User.query.filter_by(id=user_id).first()
    username = u.username
    join_date = u.created_at.strftime("%d %B %Y")

    return render_template("profile.html", username=username, join_date=join_date)


@app.route('/change_pass', methods=["GET", "POST"])
@login_required
def change_pass():
    """enables users to change passwords"""

    if request.method == "POST":

        user_id = session["user_id"]

        # check all forms filled in
        if not request.form.get("old_password") or not request.form.get("password"):
            flash("all fields must be filled out", "error")
            return redirect(url_for("change_pass"))

        # check new password fields match.
        if not request.form.get("password") == request.form.get("password-repeat"):
            flash("New Passwords don't match!", "error")
            return redirect(url_for("change_pass"))

        old_password = request.form.get("old_password")
        new_password = request.form.get("password")

        user = User.query.filter_by(id=user_id).first()

        # check old password is valid
        if not pwd_context.verify(old_password, user.hash):
            flash("Current password incorrect", "error")
            return redirect(url_for("change_pass"))

        # change password
        user.hash = pwd_context.hash(new_password)
        db.session.commit()

        flash("Password sucessfully changed!", "success")
        return redirect(url_for("profile", user_id=user_id))

    return render_template('change_pass.html')


@app.route('/delete', methods=["GET", "POST"])
@login_required
def delete():
    """deletes user and all feeds"""
    if request.method == "POST":

        # check password entered matched users
        user = User.query.filter_by(id=session["user_id"]).first()
        password = request.form.get("password")

        if not pwd_context.verify(password, user.hash):
            flash("Current password incorrect", "error")
            return redirect(url_for("profile", user_id=session["user_id"]))

        User.query.filter_by(id=session["user_id"]).delete()
        Feed.query.filter_by(user_id=session["user_id"]).delete()
        db.session.commit()

        session.clear()
        flash("User and feeds have been completely removed from our systems. Goodbye!", "success")
        return redirect(url_for("index"))

    return render_template("delete.html")


@app.route('/view/<int:feed_id>')
@login_required
def view(feed_id):
    """ page to view a rss feed """
    # get feed info.
    f = Feed.query.filter_by(id=feed_id).first()

    # check feed belongs to current user.
    if not f.user_id == session["user_id"]:
        flash("Sorry, You don't have permission to view that feed.")
        return redirect(url_for("feeds"))

    # catch old last_loaded date (if exists)
    last_loaded = f.last_loaded
    if last_loaded is None:
        last_loaded = datetime.datetime.utcnow()

    # get url and pass to get_feeds
    feed = get_feed(f.feed_url, 10, last_loaded)

    # apply new last_loaded date
    now = datetime.datetime.now()
    f.last_loaded = now
    db.session.commit()

    # sort rss feed in chronological order
    items = reversed(sorted(feed, key=lambda k: k['time']))

    return render_template("view.html", feed_title=f.feed_name, feed=items)
