from flask import Blueprint

bp = Blueprint('errors', __name__)

from server.errors import handlers
