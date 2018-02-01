from flask import redirect, render_template, request, session, url_for
from igdb_api_python.igdb import igdb
from functools import wraps
import os
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

igdb = igdb(os.environ['IGDB_API_KEY'])

def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=escape(top), bottom=escape(bottom))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)
    
def search_cache(item):
    req = cache.get(item)
    if req is None:
        req = igdb.games({
            'search': item,
            'fields': "name"
        })
        cache.set(item, req.body, timeout=5 * 60)
        return req.body
    else:
        return req