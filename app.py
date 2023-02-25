import functools
import os
import secrets
from flask import (
    Flask,
    session,
    render_template,
    request,
    abort,
    flash,
    redirect,
    url_for,
    Blueprint
)
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient

users = {}

app = Flask(__name__)
app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
)
client = MongoClient("mongodb+srv://zz3399:Zzf19971113@cluster0.zj6ekfz.mongodb.net/test")
app.db = client.eano_community


# app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        email = session.get("email")
        # if email is not None or (email not in users):
        #     return redirect(url_for("login"))
        user = app.db.users.find_one({"email": email})
        if user is None or user["token"] != session.get("token"):
            return redirect(url_for("login"))
        return route(*args, **kwargs)

    return route_wrapper


@app.route("/")
@login_required
def index():
    return render_template(
        "index.html",
        title="Eano Community"
    )


@app.route('/login', methods=["GET", "POST"])
def login():
    email = ""
    if request.method == "POST":
        email = request.form.get("login_email")
        password = request.form.get("login_password")

        # get user from db
        user = app.db.users.find_one({"email": email})
        # verify password using sha256 check if it is the same hash in db
        if pbkdf2_sha256.verify(password, user["password_hash"]):
            token = secrets.token_urlsafe(16)
            session["email"] = email
            session["token"] = token
            app.db.users.update_one(
                {"email": email},
                {"$set": {"token": token}},
                upsert=True
            )
            # generate token for login

            return redirect(url_for("index"))
        # flash("Incorrect e-mail or password.")
    return render_template("login.html", email=email)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("signup_email")
        password = request.form.get("signup_password")

        # store user {userid, email, password_hash, token} into db
        app.db.users.insert_one({
            "email": email,
            "password_hash": pbkdf2_sha256.hash(password),
        })
        # TODO handle duplicate email
        # flash("Successfully signed up")
        return redirect(url_for("login"))
    return render_template("signup.html")


if __name__ == "__main__":
    app.run()
