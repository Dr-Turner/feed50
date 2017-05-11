import html
import datetime
import time

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

# https://stackoverflow.com/questions/32911578/flask-confirm-action


def is_rss_page(url):
    """determines if a url is a valid feed or not"""
    d = feedparser.parse(url)

    return 'title' in d.feed


def get_rss_title(url):
    """returns title of rss"""
    d = feedparser.parse(url)

    return d.feed.title


def get_feed(url, n, last_loaded):
    """fetches feeds and parses them.
    :arg
        url - url of the feed
        n - number of feeds to parse
        last_loaded - datetime object of last tiem the feed was accessed. 
    """
    d = feedparser.parse(url)

    # ensure n doesn't run off the end.
    if n > len(d.entries) - 1:
        n = len(d.entries) - 1

    items = []

    for i in range(n):
        item = dict()

        item["n"] = i + 1
        item["title"] = d.entries[i].title
        item["link"] = d.entries[i].link
        item["summary"] = html.unescape(d.entries[i].summary)

        # some feeds are "updated" and some "published"
        if "updated_parsed" in d.entries[i]:
            item["time"] = datetime.datetime.fromtimestamp(time.mktime(d.entries[i].updated_parsed))
        else:
            item["time"] = datetime.datetime.fromtimestamp(time.mktime(d.entries[i].published_parsed))

        if item["time"] > last_loaded:
            item["new"] = True
        else:
            item["new"] = False

        item["time_str"] = item["time"].strftime("%d %B %Y   %H:%M:%S")

        items.append(item)

    return items
