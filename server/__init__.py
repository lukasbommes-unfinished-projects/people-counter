import os
import json
#from datetime import datetime

from flask import Flask, render_template, jsonify, Response, make_response, abort, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
#from flask_httpauth import HTTPBasicAuth

from flask_login import LoginManager, login_required, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Optional, Length, ValidationError, Email, EqualTo

from server.config import Config

# Initialization
app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()  # for user login
login_manager.init_app(app)
login_manager.login_view = "auth.login"

db = SQLAlchemy(app)

#auth = HTTPBasicAuth()  # for securing REST API


from server.models import User, Room, Camera, Count

from server.auth import bp as auth_bp
app.register_blueprint(auth_bp)#, url_prefix='/auth')

from server.setup import bp as setup_bp
app.register_blueprint(setup_bp)#, url_prefix='/auth')


# User Login & Registration

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# UI

@app.route("/")
def index():
    return render_template("index.html")



# REST API

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


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


@app.route("/people-counter/api/v1.0/counts", methods=["GET"])
#@auth.login_required
def get_counts():
    counts = []
    room_ids = [room[0] for room in db.get_rooms()]
    for room_id in room_ids:
        count = _get_count(db, room_id)
        counts.append({"room_id": room_id, "people-count": count})
    return Response(json.dumps(counts),  mimetype='application/json')


@app.route("/people-counter/api/v1.0/counts/<int:room_id>", methods=["GET"])
#@auth.login_required
def get_count(room_id):
    count = _get_count(db, room_id)
    return jsonify({"room_id": room_id, "people-count": count})

if __name__ == "__main__":
    if not os.path.exists('main.db'):
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
