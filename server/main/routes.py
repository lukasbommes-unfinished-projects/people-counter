from flask import render_template
from server.main import bp


@bp.route("/")
def index():
    return render_template("index.html")
