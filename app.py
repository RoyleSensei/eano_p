import functools
import os
import secrets
import uuid

import pymongo
from flask import (
    Flask,
    session,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
import datetime
from dateutil.relativedelta import relativedelta
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

users = {}

app = Flask(__name__)
app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", secrets.token_urlsafe(16)
)
client = MongoClient(os.getenv("MONGODB_URI"))
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


def admin_login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        email = session.get("email")
        admin = app.db.admins.find_one({"email": email})
        if admin is None or admin["token"] != session.get("token"):
            return redirect(url_for("admin_login"))
        return route(*args, **kwargs)

    return route_wrapper


@app.route("/", methods=["GET"])
@login_required
def index():
    nav = request.args.get("nav") if "nav" in request.args else "latest"
    if nav == "latest":
        posts = app.db.posts.find().sort('date', pymongo.DESCENDING)
    elif nav == "most_liked":
        posts = app.db.posts.find().sort('likes_count', pymongo.DESCENDING)
    elif nav == "highest_rated":
        posts = app.db.posts.find().sort('highest_rated', pymongo.DESCENDING)
    else:
        posts = []

    return render_template(
        "index.html",
        title="Eano Community",
        session=session,
        post_cards=posts
    )


@app.route('/login/', methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form.get("login_email")
        password = request.form.get("login_password")

        # get user from db
        user = app.db.users.find_one({"email": email})

        if user is None:
            message = "Wrong email or password!"
            return render_template("login.html", message=message)
        # verify password using sha256 check if it is the same hash in db
        if pbkdf2_sha256.verify(password, user["password_hash"]):
            # generate token for login
            token = secrets.token_urlsafe(16)
            session["uid"] = str(user["_id"])
            session["username"] = user["username"]
            session["avatar_url"] = user["avatar_url"]
            session["email"] = email
            session["token"] = token
            app.db.users.update_one(
                {"email": email},
                {"$set": {"token": token}},
                upsert=True
            )
            return redirect(url_for("index"))
        else:
            message = "Wrong email or password!"
            return render_template("login.html", message=message)

    return render_template("login.html", message=message)


@app.route('/signup/', methods=["GET", "POST"])
def signup():
    message = {}
    if request.method == "POST":
        username = request.form.get("signup_username")
        email = request.form.get("signup_email")
        password = request.form.get("signup_password")
        confirmed_password = request.form.get("signup_confirm_password")
        if confirmed_password == password:
            pass
        else:
            message["confirmed_password"] = "Password does not match!"
            return render_template("signup.html", message=message)

        existed_user = app.db.users.find_one({"email": email})
        if existed_user is None:
            # store user {userid, email, password_hash, token} into db
            app.db.users.insert_one({
                "username": username,
                "email": email,
                "password_hash": pbkdf2_sha256.hash(password),
                "avatar_url": "/static/img/av.png",
                "created_time": datetime.datetime.now()
            })
            return redirect(url_for("login"))
        else:
            message["email"] = "Email already exists!"
            return render_template("signup.html", message=message)

    return render_template("signup.html", message=message)


@app.route("/logout")
def logout():
    app.db.users.update_one({"email": session["email"]},
                            {"$set": {"token": ""}},
                            upsert=True
                            )
    return redirect(url_for("login"))


@app.route("/admin_logout")
def admin_logout():
    app.db.admins.update_one({"email": session["email"]},
                             {"$set": {"token": ""}},
                             upsert=True
                             )
    return redirect(url_for("admin_login"))


@app.route('/user_profile/', methods=["GET", "POST"])
@login_required
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
        kwargs["avatar_url"] = "/static/img/av.png"
    if "posts" not in kwargs or kwargs["posts"] is None:
        kwargs["post_cards"] = []
    else:
        post_cards = []
        for pid in user["posts"]:
            post_card = app.db.posts.find_one({"_id": ObjectId(pid)})
            post_cards += [post_card]
        kwargs["post_cards"] = post_cards

    if "followers" not in kwargs or kwargs["followers"] is None:
        kwargs["follower_cards"] = []
    else:
        follower_cards = []
        for uid in user["followers"]:
            follower_card = app.db.users.find_one({"_id": ObjectId(uid)})
            follower_cards += [follower_card]
        kwargs["follower_cards"] = follower_cards

    if "followings" not in kwargs or kwargs["followings"] is None:
        kwargs["following_cards"] = []
    else:
        following_cards = []
        for uid in user["followings"]:
            following_card = app.db.users.find_one({"_id": ObjectId(uid)})
            following_cards += [following_card]
        kwargs["following_cards"] = following_cards

    if "likes" not in kwargs or kwargs["likes"] is None:
        kwargs["liked_cards"] = []
    else:
        liked_cards = []
        for pid in user["likes"]:
            liked_card = app.db.posts.find_one({"_id": ObjectId(pid)})
            if liked_card is not None:
                liked_cards += [liked_card]
        kwargs["liked_cards"] = liked_cards

    return render_template(
        "user_profile.html", **kwargs
    )


@app.route('/user_profile/avatar/', methods=["POST"])
@login_required
def upload_avatar():
    target = os.path.join(APP_ROOT, 'static/img/avatars/')  # folder_path
    if not os.path.isdir(target):
        os.mkdir(target)  # create folder if not exists

    new_filename = None
    for file in request.files.getlist("user_profile_avatar"):
        suffix = secure_filename(file.filename).split(".")[-1]
        new_filename = str(session["uid"]) + "." + suffix
        if os.path.exists(target + new_filename):
            os.remove(target + new_filename)
        file.save(target + new_filename)

    app.db.users.update_one(
        {"email": session["email"]},
        {"$set": {
            "avatar_url": '/static/img/avatars/' + new_filename}},
        upsert=True)
    session["avatar_url"] = '/static/img/avatars/' + new_filename

    return redirect(url_for("user_profile"))


@app.route('/post/create', methods=["GET", "POST"])
@login_required
def post_create():
    target = os.path.join(APP_ROOT, 'static/img/post_img/')  # folder_path
    if not os.path.isdir(target):
        os.mkdir(target)  # create folder if not exists

    if request.method == "POST":
        post_img_filename = None
        for file in request.files.getlist("user_post_img"):
            suffix = secure_filename(file.filename).split(".")[-1]
            post_img_filename = str(uuid.uuid4()) + "." + suffix
            file.save(target + post_img_filename)

        insert_result = app.db.posts.insert_one({
            "post_img_url": '/static/img/post_img/' + post_img_filename,
            "author_id": session["uid"],
            "author": session["username"],
            "author_avatar_url": session["avatar_url"]
        })

        pid = str(insert_result.inserted_id)
        user = app.db.users.find_one({"email": session["email"]})
        app.db.users.update_one(
            {"email": session["email"]},
            {"$set": {
                "posts": (user["posts"] if "posts" in user else []) + [pid]
            }},
            upsert=True
        )
        return redirect(url_for("post_create_continue", pid=pid))
    return render_template("post_create.html", session=session)


@app.route('/post/create/<pid>', methods=["GET", "POST"])
@login_required
def post_create_continue(pid):
    post = app.db.posts.find_one({"_id": ObjectId(pid)})

    if request.method == "POST":
        if len(request.files) == 0:
            if "cancel" in request.form:
                return redirect(url_for("user_profile", nav="posts"))
            else:
                rating = request.form.get("user_post_rating")
                title = request.form.get("user_post_title")
                review = request.form.get("user_post_review")
                formatted_date = datetime.datetime.today().strftime("%Y-%m-%d-%H:%M:%S")
                app.db.posts.update_one(
                    {"_id": ObjectId(pid)},
                    {"$set": {
                        "rating": rating,
                        "title": title,
                        "review": review,
                        "date": formatted_date
                    }},
                    upsert=True
                )
                return redirect(url_for("user_profile", nav="posts", session=session))
        else:
            target = os.path.join(APP_ROOT, 'static/img/post_img/')  # folder_path
            if not os.path.isdir(target):
                os.mkdir(target)  # create folder if not exists
            post_img_filename = None
            for file in request.files.getlist("user_post_img"):
                suffix = secure_filename(file.filename).split(".")[-1]
                post_img_filename = str(uuid.uuid4()) + "." + suffix
                file.save(target + post_img_filename)

            app.db.posts.update_one(
                {"_id": ObjectId(pid)},
                {"$set": {
                    "post_img_url": '/static/img/post_img/' + post_img_filename
                }}
            )
            post["post_img_url"] = '/static/img/post_img/' + post_img_filename
            return render_template("post_continue.html", session=session, post_card=post)

    else:  # method == "GET"
        return render_template("post_continue.html", session=session, post_card=post)


@app.route('/post/<pid>', methods=["GET", "POST"])
@login_required
def post_management(pid):
    post = app.db.posts.find_one({"_id": ObjectId(pid)})
    user = app.db.users.find_one({"email": session["email"]})

    liked = "false"
    if "likes" in user and pid in user["likes"]:
        liked = "true"

    if request.method == "POST":
        if "delete" in request.form:
            app.db.posts.delete_one(
                {"_id": ObjectId(pid)}
            )
            user = app.db.users.find_one(
                {"email": session["email"]}
            )
            user["posts"].remove(pid)
            app.db.users.update_one(
                {"email": session["email"]},
                {"$set": {
                    "posts": user["posts"]
                }}
            )
            return redirect(url_for("user_profile", nav="posts"))

    elif request.method == "GET":
        return render_template("post.html", session=session, post_card=post, user_card=user, liked=liked)


@app.route('/post/like/<pid>', methods=["POST"])
def liked_posts(pid):
    if "like" in request.form:
        current_user = app.db.users.find_one({'email': session["email"]})
        app.db.users.update_one(
            {"email": session["email"]},
            {"$set": {
                "likes": (current_user["likes"] if "likes" in current_user else []) + [pid]
            }},
            upsert=True
        )
        post = app.db.posts.find_one({"_id": ObjectId(pid)})
        app.db.posts.update_one(
            {"_id": ObjectId(pid)},
            {"$set": {
                "likes_count": (post["likes_count"] if "likes_count" in post else 0) + 1
            }}
        )
        return redirect('/post/' + pid)
    elif "unlike" in request.form:
        current_user = app.db.users.find_one({'email': session["email"]})
        current_user["likes"].remove(pid)
        app.db.users.update_one(
            {"email": session["email"]},
            {"$set": {
                "likes": current_user["likes"]
            }}
        )
        post = app.db.posts.find_one({"_id": ObjectId(pid)})
        app.db.posts.update_one(
            {"_id": ObjectId(pid)},
            {"$set": {
                "likes_count": post["likes_count"] - 1
            }}
        )
        return redirect('/post/' + pid)


@app.route('/search', methods=["POST", "GET"])
@login_required
def search_result():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        return redirect("/search?nav=posts&keyword=" + keyword)
    else:
        nav = request.args.get("nav")
        if nav is None:
            nav = "posts"

        keyword = request.args.get("keyword")
        if keyword is None:
            keyword = ""
        post_cards = [_ for _ in app.db.posts.find({"title": {'$regex': ".*" + keyword + ".*", "$options": "i"}})]
        user_cards = [_ for _ in app.db.users.find({"username": {'$regex': ".*" + keyword + ".*", "$options": "i"}})]

        return render_template("search_result.html", nav=nav, keyword=keyword, post_cards=post_cards,
                               user_cards=user_cards,
                               session=session)


@app.route('/user/<uid>', methods=["POST", "GET"])
@login_required
def user_main_page(uid):
    user = app.db.users.find_one({"_id": ObjectId(uid)})

    post_cards = []
    if "posts" in user:
        for pid in user["posts"]:
            post_card = app.db.posts.find_one({"_id": ObjectId(pid)})
            post_cards.append(post_card)

    nav = request.args.get("nav")
    if nav is None:
        nav = "posts"

    followed = "false"
    if "followers" in user and session["uid"] in user["followers"]:
        followed = "true"

    follower_cards = []
    if "followers" in user:
        for follower_id in user["followers"]:
            follower_cards.append(
                app.db.users.find_one({"_id": ObjectId(follower_id)})
            )

    following_cards = []
    if "followings" in user:
        for following_id in user["followings"]:
            following_cards.append(
                app.db.users.find_one({"_id": ObjectId(following_id)})
            )

    liked_cards = []
    if "likes" in user:
        for pid in user["likes"]:
            liked_cards.append(
                app.db.posts.find_one({"_id": ObjectId(pid)})
            )

    return render_template('user_main.html', post_cards=post_cards, user=user, followed=followed, nav=nav,
                           follower_cards=follower_cards, following_cards=following_cards, liked_cards=liked_cards)


@app.route('/user/follow/<uid>', methods=["POST"])
def follow(uid):
    if "follow" in request.form:
        current_user = app.db.users.find_one({'email': session["email"]})
        app.db.users.update_one(
            {"email": session["email"]},
            {"$set": {
                "followings": (current_user["followings"] if "followings" in current_user else []) + [uid]
            }},
            upsert=True
        )
        following_user = app.db.users.find_one({"_id": ObjectId(uid)})
        app.db.users.update_one(
            {"_id": ObjectId(uid)},
            {"$set": {
                "followers": (following_user["followers"] if "followers" in following_user else []) + [session["uid"]],
                "followers_count": (following_user["followers_count"] if "followers_count" in following_user else 0) + 1
            }},
            upsert=True
        )

    else:
        current_user = app.db.users.find_one({'email': session["email"]})
        current_user["followings"].remove(uid)
        app.db.users.update_one(
            {"email": session["email"]},
            {"$set": {
                "followings": current_user["followings"]
            }}
        )
        unfollowing_user = app.db.users.find_one({"_id": ObjectId(uid)})
        unfollowing_user["followers"].remove(session["uid"])
        app.db.users.update_one(
            {"_id": ObjectId(uid)},
            {"$set": {
                "followers": (unfollowing_user["followers"]),
                "followers_count": unfollowing_user["followers_count"] - 1
            }},
        )
    return redirect('/user/' + uid)


@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    message = ""
    if request.method == "POST":
        email = request.form.get("admin_login_email")
        password = request.form.get("admin_login_password")

        # get admin from db
        admin = app.db.admins.find_one({"email": email})

        if admin is None:
            message = "Wrong email or password!"
            return render_template("admin_login.html", message=message)
        # verify password using sha256 check if it is the same hash in db
        if pbkdf2_sha256.verify(password, admin["password_hash"]):
            # generate token for login
            token = secrets.token_urlsafe(16)
            session["uid"] = str(admin["_id"])
            session["username"] = admin["username"]
            session["avatar_url"] = admin["avatar_url"]
            session["email"] = email
            session["token"] = token
            app.db.admins.update_one(
                {"email": email},
                {"$set": {"token": token}},
                upsert=True
            )
            return redirect(url_for("admin_pages"))
        else:
            message = "Wrong email or password!"
            return render_template("admin_login.html", message=message)

    return render_template("admin_login.html", message=message)


def add_user_growth_chart(admin_data):
    admin_data["user_growth_chart"] = {
        "months": [],
        "users_number": [],
    }

    def get_recent_6_months():
        res = []
        start_date = datetime.datetime.today() + relativedelta(months=1)
        start_date = datetime.datetime(year=start_date.year, month=start_date.month, day=1)
        for i in range(6):
            res.insert(0, start_date + relativedelta(months=-i))
        return res

    for date in get_recent_6_months():
        count = app.db.users.count_documents({
            "created_time": {
                "$lt": date
            }
        })
        admin_data["user_growth_chart"]["months"].append(date.strftime("%Y-%m"))
        admin_data["user_growth_chart"]["users_number"].append(count)


def add_user_location_chart(admin_data):
    agg_result = app.db.users.aggregate(
        [{
            "$group":
                {"_id": "$state",
                 "value": {"$sum": 1}
                 }}
        ])
    data = ""
    for row in agg_result:
        if row['_id'] is None:
            row['_id'] = 'Unknown'
        data += "{" + "name: '{}', value: {}".format(row['_id'], row['value']) + "},"
    data = "[" + data + "]"
    admin_data["user_location_graph"] = data


def add_user_age_chart(admin_data):
    admin_data["user_age_chart"] = {}
    all_users = [u for u in app.db.users.find({}) if "birthday" in u and u["birthday"] is not None]
    for user in all_users:
        user["age"] = relativedelta(
            datetime.datetime.now(),
            datetime.datetime.strptime(user["birthday"], "%Y-%m-%d")
        ).years

    ages_counter = {}
    for user in all_users:
        if user["age"] in ages_counter:
            ages_counter[user["age"]] += 1
        else:
            ages_counter[user["age"]] = 1
    admin_data["user_age_chart"]["ages"] = [_ for _ in ages_counter.keys()]
    admin_data["user_age_chart"]["counts"] = [_ for _ in ages_counter.values()]


def add_post_growth_chart(admin_data):
    admin_data["post_growth_chart"] = {
        "months": [],
        "posts_number": [],
    }

    def get_recent_6_months():
        res = []
        start_date = datetime.datetime.today() + relativedelta(months=1)
        start_date = datetime.datetime(year=start_date.year, month=start_date.month, day=1)
        for i in range(6):
            res.insert(0, start_date + relativedelta(months=-i))
        return res

    for date in get_recent_6_months():
        count = app.db.posts.count_documents({
            "date": {
                "$lt": date.strftime("%Y-%m")
            }
        })
        admin_data["post_growth_chart"]["months"].append(date.strftime("%Y-%m"))
        admin_data["post_growth_chart"]["posts_number"].append(count)


def add_post_rating_chart(admin_data):
    agg_rating_result = app.db.posts.aggregate(
        [{
            "$group":
                {"_id": "$rating",
                 "value": {"$sum": 1}
                 }}
        ])
    data = ""
    for row in agg_rating_result:
        if row['_id'] is None:
            row['_id'] = 'Unknown'
        data += "{" + "name: '{}', value: {}".format(row['_id'], row['value']) + "},"
    data = "[" + data + "]"
    admin_data["post_rating_chart"] = data


@app.route('/admin', methods=['GET', 'POST'])
@admin_login_required
def admin_pages():
    nav = request.args.get("nav") if "nav" in request.args else "dashboard"
    admin_data = {}

    if nav == "dashboard":
        admin_data["users_number"] = app.db.users.count_documents({})
        admin_data["posts_number"] = app.db.posts.count_documents({})
        add_user_growth_chart(admin_data)
        add_post_growth_chart(admin_data)
        return render_template('admin_page.html', admin_data=admin_data, nav=nav)

    elif nav == "users":
        admin_data["users_number"] = app.db.users.count_documents({})
        keyword = request.args.get("keyword")
        if keyword is None:
            keyword = ""
        user_cards = [_ for _ in app.db.users.find({"username": {'$regex': ".*" + keyword + ".*", "$options": "i"}})]
        admin_data["user_search_result"] = user_cards
        add_user_growth_chart(admin_data)
        add_user_age_chart(admin_data)
        add_user_location_chart(admin_data)
        return render_template("admin_page.html", nav=nav, admin_data=admin_data)

    elif nav == "posts":
        admin_data["posts_number"] = app.db.posts.count_documents({})

        keyword = request.args.get("keyword")
        if keyword is None:
            keyword = ""
        post_cards = [_ for _ in app.db.posts.find({"title": {'$regex': ".*" + keyword + ".*", "$options": "i"}})]
        admin_data["post_search_result"] = post_cards
        add_post_growth_chart(admin_data)
        add_post_rating_chart(admin_data)
        return render_template("admin_page.html", nav=nav, admin_data=admin_data)

    else:
        pass


@app.route('/admin_user_search', methods=["POST"])
@admin_login_required
def admin_user_search_result():
    keyword = request.form.get("keyword")
    return redirect("/admin?nav=users&keyword=" + keyword)


@app.route('/admin_post_search', methods=["POST"])
@admin_login_required
def admin_post_search_result():
    keyword = request.form.get("keyword")
    return redirect("/admin?nav=posts&keyword=" + keyword)


if __name__ == "__main__":
    app.run()
