# import logging
# setup logging
# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

from functools import wraps
from flask import session, redirect, url_for, request, flash

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



