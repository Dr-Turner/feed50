from functools import wraps
from flask import session, redirect, url_for, request, flash
import feedparser


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You must be logged in to view this page!", "error")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def is_rss_page(url):
    """determines if a url is a valid feed or not"""
    d = feedparser.parse(url)

    return 'title' in d.feed


def get_rss_title(url):
    """returns title of rss"""
    d = feedparser.parse(url)

    return d.feed.title
