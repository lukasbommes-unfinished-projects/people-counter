from flask import Blueprint

bp = Blueprint("setup", __name__)

from server.setup import routes, forms
