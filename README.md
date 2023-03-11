## Project: Online Community Website For Eano Home Renovations
______

### Project Overview
- **Website Pages:**
  - Timeline Page
  - User sign-in and sign-up pages
  - User profile page
    - Subpages:
      - CreatedPosts page
      - LikedPosts page
      - Followings page
      - Followers page
      - ProfileEdit page
  - PostCreation page
  - PostShow page
  - User public main page
  

- **Project Description**

    - This website development project aims to increase customer relations quality. This website will operate as an
      online memo for registered customers. Registered customers can
      create their posts based on the home design they reviewed. Specifically, they can personalize their posts by
      adding pictures, website links, and captions on this new website. Moreover, they can also rate those posts they
      created to
      show their home design preferences. All the registered users’ posts will be presented on
      the Timeline page for everyone to view.

    - > Eano is a construction technology company founded in 2019 that provides highly
      standardized processes and advanced communication between homeowners,
      architects, and contractors. The service provided by Eano is majorly online. For
      homeowners, Eano aims to deliver reliable custom design and build solutions. For
      architects, Eano provides tools to help them efficiently reach and understand more
      customers. Therefore, customer relations management and engagement are two
      required sources for Eano. These become the major tasks of this website development project.
      

____

### Project Presentation

- **Login Page**

    ![Login Page.jpg](static%2Fimg%2FprojectPresentation%2FLogin%20Page.jpg)

_**Description:**_ Login page contains email & password verification methods. 

- Backend Code:

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


- Implementation of MongoDB database

        app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
        app.config["SECRET_KEY"] = os.environ.get(
            "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
        )
        client = MongoClient("mongodb+srv://zz3399:Zzf19971113@cluster0.zj6ekfz.mongodb.net/test")
        app.db = client.eano_community

<br/>

- **Sign-up Page**
![Sign-up Page.jpg](static%2Fimg%2FprojectPresentation%2FSign-up%20Page.jpg)

_**Description:**_ Users can sign up their accounts with their email. This page contains duplicate email control and the
password confirming method.

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
                    "avatar_url": "/static/img/av.png"
                })
                return redirect(url_for("login"))
            else:
                message["email"] = "Email already exists!"
                return render_template("signup.html", message=message)
    
        return render_template("signup.html", message=message)

<br/>

- **Timeline Page**
![TimeLinePage.jpg](static%2Fimg%2FprojectPresentation%2FTimeLinePage.jpg)

_**Description:**_ Contains posts created by users. There are three opions including **Latest**, **Most Liked**, and 
**Highest Rated** for users to filter the posts.

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

<br/>

- **PostShow Page**
![PostShow Page.jpg](static%2Fimg%2FprojectPresentation%2FPostShow%20Page.jpg)

_**Description:**_ Users can view the posts published by themselves or others and choose to like the post or not. Users
can also click on the author username to go to the author's main page. 

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

<br/>

- **Search result Pages**