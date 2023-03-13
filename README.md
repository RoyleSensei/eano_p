# Project: Online Community Website For Eano Home Renovations
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
  
<br/>

- **Project Description**

    - This website development project aims to increase customer relations quality. This website will operate as an
      online memo for registered customers. Registered customers can
      create their posts based on the home design they reviewed. Specifically, they can personalize their posts by
      adding pictures, website links, and captions on this new website. Moreover, they can also rate those posts they
      created to
      show their home design preferences. All the registered users’ posts will be presented on
      the Timeline page for everyone to view.

    > Eano is a construction technology company founded in 2019 that provides highly
      standardized processes and advanced communication between homeowners,
      architects, and contractors. The service provided by Eano is majorly online. For
      homeowners, Eano aims to deliver reliable custom design and build solutions. For
      architects, Eano provides tools to help them efficiently reach and understand more
      customers. Therefore, customer relations management and engagement are two
      required sources for Eano. These become the major tasks of this website development project.

  
<br/>

## Installation and Usage

----
### Installation

This project requires Python 3.10 to run. Also, it requires Flask with the Jinja2 template language. The backend database
of this project uses MongoDB. 

**To get started:**

>pip install Flask

    import pymongo
    from flask import (
        Flask,
        session,
        render_template,
        request,
        redirect,
        url_for,
    )
    from pymongo import MongoClient
    from werkzeug.utils import secure_filename
    from bson.objectid import ObjectId

**Setup MongoDb:**

    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
    )
    client = MongoClient("mongodb+srv://username:password@cluster0.zj6ekfz.mongodb.net/xxx")
    app.db = client.eano_community



<br/>

## Project Presentation

---

- **Login Page**

    ![Login Page.jpg](static%2Fimg%2FprojectPresentation%2FLogin%20Page.jpg?raw=true)

_**Description:**_ Login page contains email & password verification methods. 


<br/>

- **Sign-up Page**
![Sign-up Page.jpg](static%2Fimg%2FprojectPresentation%2FSign-up%20Page.jpg?raw=true)

_**Description:**_ Users can sign up their accounts with their email. This page contains duplicate email control and the
password confirming method.

  
<br/>

- **Timeline Page**
![TimeLinePage.jpg](static%2Fimg%2FprojectPresentation%2FTimeLinePage.jpg?raw=true)

_**Description:**_ Contains posts created by users. There are three opions including **Latest**, **Most Liked**, and 
**Highest Rated** for users to filter the posts.


<br/>

- **PostShow Page**
![PostShow Page.jpg](static%2Fimg%2FprojectPresentation%2FPostShow%20Page.jpg?raw=true)

_**Description:**_ Users can view the posts published by themselves or others and choose to like the post or not. Users
can also click on the author username to go to the author's main page. 

  

<br/>

- **Search result Pages**

    ![SearchResult_1.jpg](static%2Fimg%2FprojectPresentation%2FSearchResult_1.jpg?raw=true)

    ![SearchResult_2.jpg](static%2Fimg%2FprojectPresentation%2FSearchResult_2.jpg?raw=true)

_**Description:**_ Users can use search bar to find other users or other specific posts.

   

<br/>

- **Post Create Pages**
![PostCreate_1.jpg](static%2Fimg%2FprojectPresentation%2FPostCreate_1.jpg)
![PostCreate_2.jpg](static%2Fimg%2FprojectPresentation%2FPostCreate_2.jpg)

_**Description:**_ Users can create post by submitting a picture and then rate, edit, or update their posts.

   

<br/>

- **Logout Modal**
![LogoutModal.jpg](static%2Fimg%2FprojectPresentation%2FLogoutModal.jpg)

_**Description:**_ Users can log out their accounts by clicking the button in the upper-right corner. 


<br/>

- **UserProfile Posts Page**- 

  ![UserProfile_Posts.jpg](static%2Fimg%2FprojectPresentation%2FUserProfile_Posts.jpg)

  - _**Description:**_ Users can view the posts they create on this subpage. Users can edit and delete the posts they created.

  <br/>
  
  ![UserProfile_LikedPosts.jpg](static%2Fimg%2FprojectPresentation%2FUserProfile_LikedPosts.jpg)

- _**Description:**_ Users can view the posts they liked.

  <br/>
  
  ![UserProfile_Followings.jpg](static%2Fimg%2FprojectPresentation%2FUserProfile_Followings.jpg)

- _**Description:**_ Users can view the accounts they are following.

  <br/>
  
  ![UserProfile_Followers.jpg](static%2Fimg%2FprojectPresentation%2FUserProfile_Followers.jpg)

- _**Description:**_ Users can view their followers.

  <br/>
  
  ![UserProfile_EditProfile.jpg](static%2Fimg%2FprojectPresentation%2FUserProfile_EditProfile.jpg)

- _**Description:**_ Users can edit their profile information and update their avatar.

  
  <br/>

- **UserProfile Public Main Pages** 

    ![UserPublicMainPage_1.jpg](static%2Fimg%2FprojectPresentation%2FUserPublicMainPage_1.jpg)
    ![UserPublicMainPage_2.jpg](static%2Fimg%2FprojectPresentation%2FUserPublicMainPage_2.jpg)

- _**Description:**_ Users can follow or unfollow the accounts. Users can view the posts created by the specific user, 
the posts liked by the specific user, the following accounts and followers of the specific user, and the basic profile info
of the specific user.


