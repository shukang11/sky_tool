from flask import render_template, Blueprint

page = Blueprint("page", __name__)

@page.route("/")
def index():
    return render_template("index.html")