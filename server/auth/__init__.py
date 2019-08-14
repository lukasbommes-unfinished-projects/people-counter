from flask import Blueprint

bp = Blueprint("auth", __name__)

from server.auth import routes
