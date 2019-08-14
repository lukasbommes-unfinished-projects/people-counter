import os
import json
from flask import Flask, jsonify, Response, abort
from flask_sqlalchemy import SQLAlchemy
#from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from server.config import Config

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()  # for user login
login_manager.login_view = "auth.login"
login_manager.init_app(app)
db = SQLAlchemy(app)

#auth = HTTPBasicAuth()  # for securing REST API

from server.main import bp as main_bp
app.register_blueprint(main_bp)

from server.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from server.auth import bp as auth_bp
app.register_blueprint(auth_bp)

from server.setup import bp as setup_bp
app.register_blueprint(setup_bp)

if not os.path.exists('main.db'):
    db.create_all()

# REST API

# @app.route("/people-counter/api/v1.0/rooms", methods=["GET"])
# #@auth.login_required
# def get_rooms():
#     rooms = Room.query.all()
#     if not rooms:
#         abort(404)
#     return Response(json.dumps([room.to_dict() for room in rooms]),  mimetype='application/json')
#
#
# @app.route("/people-counter/api/v1.0/rooms/<int:room_id>", methods=["GET"])
# #@auth.login_required
# def get_room(room_id):
#     room = Room.query.get(room_id)
#     if not room:
#         abort(404)
#     return Response(json.dumps(room.to_dict()),  mimetype='application/json')


# @app.route("/people-counter/api/v1.0/counts", methods=["GET"])
# #@auth.login_required
# def get_counts():
#     counts = []
#     room_ids = [room[0] for room in db.get_rooms()]
#     for room_id in room_ids:
#         count = _get_count(db, room_id)
#         counts.append({"room_id": room_id, "people-count": count})
#     return Response(json.dumps(counts),  mimetype='application/json')
#
#
# @app.route("/people-counter/api/v1.0/counts/<int:room_id>", methods=["GET"])
# #@auth.login_required
# def get_count(room_id):
#     count = _get_count(db, room_id)
#     return jsonify({"room_id": room_id, "people-count": count})
