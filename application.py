from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from pymongo.collection import ReturnDocument

from helpers import *
from mongo import *

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
        result = db_search(request.form.get("username"))
        # ensure username exists and password is correct
        if result is None or not pwd_context.verify(request.form.get("password"), result["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = result["_id"]

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
        
        # create user object
        user = User(request.form.get("username"), hash)
        
        # store info in database
        result = db_insert_user(user)

        if not result.acknowledged:
            return apology("error")

        # log user in
        session["user_id"] = result.inserted_id

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
        
        # check if query is already cached. request is sent automatically if not in cache
        query = search_cache(str(request.form.get("query")))
        
        lists = db_get_lists(session["user_id"])
        return render_template("results.html", result = query, lists = lists["lists"])

    # else if reached via GET
    else:
        return render_template("search.html")
        
@app.route("/lists", methods=["GET", "POST"])
@login_required
def lists():
    # if reached via POST
    if request.method == "POST":
        
        # get name of new list
        name = request.form.get("new_list_name")
        
        # connect to db and make the new list
        db = client.test_db
        result = db.users.find_one_and_update(
            {"_id": session["user_id"]},
            {"$push": { "lists": {"name": name, "items": []}}},
            projection={"lists": True},
            return_document=ReturnDocument.AFTER)
        return render_template("lists.html", lists = result["lists"])

    # else if reached via GET
    else:
        
        # query database for existing lists and return them for display
        result = db_get_lists(session["user_id"])
        print(result)
        return render_template("lists.html", lists = result["lists"])

@app.route("/add", methods=["POST"])
@login_required
def add():
    # if reached via POST
    if request.method == "POST":
        
        # get list and item info from request
        req = request.form.copy()
        list_arr = req.poplist("lists")
        game = req.popitem()
        
        # find the list(s) and add info
        db = client.test_db
        for name in list_arr:
            result = db.users.find_one_and_update(
                {"_id": session["user_id"]},
                {"$push": { "lists.$[t].items": {"id": game[0], "name": game[1]}}},
                projection={"lists": True},
                return_document=ReturnDocument.AFTER,
                arrayFilters=[{"t.name": name}])
            
        # redirect user to lists
        return redirect(url_for("lists"))
        
    # else if reached via GET
    else:
        # redirect user to home page
        return redirect(url_for("index"))
        
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))