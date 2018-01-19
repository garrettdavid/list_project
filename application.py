from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from igdb_api_python.igdb import igdb
import os

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

igdb = igdb(os.environ['IGDB_API_KEY'])

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    # if user reached route via POST
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("missing username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("missing password")

        # ensure password confirmation was submitted
        elif not request.form.get("password_confirm"):
            return apology("missing password confirmation")

        # ensure password and password_confirm match
        elif request.form.get("password") != request.form.get("password_confirm"):
            return apology("passwords do not match")

        # hash password
        hash = pwd_context.hash(request.form.get("password"))

        # store info in database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username = request.form.get("username"), hash = hash)

        if not result:
            return apology("username already exists")

        # log user in
        session["user_id"] = result

        #redirect to home page
        return redirect(url_for("index"))

    # else if user reached route via GET
    else:
        return render_template("register.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    # if reached via POST
    if request.method == "POST":

        query = request.form.get("query")

        result = igdb.games({
            'search': query,
            'fields': "name"
        })

        return render_template("results.html", result = result.body)

    # else if reached via GET
    else:
        return render_template("search.html")