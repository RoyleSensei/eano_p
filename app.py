from flask import Flask, render_template, Blueprint, request

app = Flask(__name__)


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print(request.form)
    return render_template("login.html")


if __name__ == '__main__':
    app.run()
