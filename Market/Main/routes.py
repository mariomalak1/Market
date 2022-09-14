from Market import app
from flask import render_template, Blueprint
from flask_login import login_required

# application's code here

main = Blueprint("main", __name__)

@main.route('/')
@main.route("/home")
@login_required
def home():
    return render_template("main/home.html", title ="home", page_title ="")
