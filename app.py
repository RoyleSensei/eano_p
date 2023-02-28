import functools
import os
import secrets
import uuid
from flask import (
    Flask,
    session,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient
from werkzeug.utils import secure_filename

users = {}

app = Flask(__name__)
app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
)
client = MongoClient("mongodb+srv://zz3399:Zzf19971113@cluster0.zj6ekfz.mongodb.net/test")
app.db = client.eano_community

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


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
        title="Eano Community",
        username=session["username"]
    )


@app.route('/login/', methods=["GET", "POST"])
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
            session["username"] = user["username"]
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


@app.route('/signup/', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("signup_username")
        email = request.form.get("signup_email")
        password = request.form.get("signup_password")

        # store user {userid, email, password_hash, token} into db
        app.db.users.insert_one({
            "username": username,
            "email": email,
            "password_hash": pbkdf2_sha256.hash(password),
        })
        # TODO handle duplicate email
        # flash("Successfully signed up")
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route('/user_profile/', methods=["GET", "POST"])
def user_profile():
    nav = request.args.get("nav")
    if nav is None:
        nav = "posts"

    if request.method == "POST":
        username = request.form.get("user_profile_username")
        firstname = request.form.get("user_profile_firstname")
        lastname = request.form.get("user_profile_lastname")
        birthday = request.form.get("user_profile_birthday")
        address1 = request.form.get("user_profile_address1")
        address2 = request.form.get("user_profile_address2")
        city = request.form.get("user_profile_city")
        state = request.form.get("user_profile_state")
        zipcode = request.form.get("user_profile_zip")
        aboutyou = request.form.get("user_profile_aboutyou")


        app.db.users.update_one(
            {"email": session["email"]},
            {"$set": {
                "username": username,
                "firstname": firstname,
                "lastname": lastname,
                "birthday": birthday,
                "address1": address1,
                "address2": address2,
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "aboutyou": aboutyou
            }},
            upsert=True
        )

    kwargs = user = app.db.users.find_one({"email": session["email"]})
    kwargs["nav"] = nav
    if "firstname" not in kwargs or kwargs["firstname"] is None:
        kwargs["firstname"] = "John"
    if "lastname" not in kwargs or kwargs["lastname"] is None:
        kwargs["lastname"] = "Smith"
    if "address1" not in kwargs or kwargs["address1"] is None:
        kwargs["address1"] = "111 Becker St."
    if "city" not in kwargs or kwargs["city"] is None:
        kwargs["city"] = "City you live in..."
    if "state" not in kwargs or kwargs["state"] is None:
        kwargs["state"] = "Choose..."
    if "aboutyou" not in kwargs or kwargs["aboutyou"] is None:
        kwargs["aboutyou"] = "How you feel..."

    if "avatar_url" not in kwargs or kwargs["avatar_url"] is None:
        kwargs["avatar_url"] = "../static/img/av.png"

    return render_template(
        "user_profile.html", **kwargs
    )


@app.route('/user_profile/avatar/', methods=["POST"])
def upload_avatar():
    target = os.path.join(APP_ROOT, 'static/img/avatars/')  # folder_path
    if not os.path.isdir(target):
        os.mkdir(target)  # create folder if not exists

    new_filename = None
    for file in request.files.getlist("user_profile_avatar"):
        suffix = secure_filename(file.filename).split(".")[-1]
        new_filename = str(uuid.uuid4()) + "." + suffix
        file.save(target + new_filename)

    app.db.users.update_one(
        {"email": session["email"]},
        {"$set": {
            "avatar_url":  '../static/img/avatars/' + new_filename}},
        upsert=True)

    return redirect(url_for("user_profile"))


@app.route('/post_creation')
def create_post():
    pass


if __name__ == "__main__":
    app.run()
