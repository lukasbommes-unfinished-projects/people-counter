import os
import json
#from datetime import datetime

from flask import Flask, render_template, jsonify, Response, make_response, abort, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
#from flask_httpauth import HTTPBasicAuth

from flask_login import LoginManager, login_required, login_user, logout_user, current_user

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



class RoomForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=64)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=400)])
    submit = SubmitField("Save changes")


class CameraForm(FlaskForm):
    url = StringField("URL", validators=[InputRequired(), Length(max=256)])
    username = StringField("Username", validators=[Optional(), Length(max=64)])
    password = PasswordField("Password", validators=[Optional(), Length(max=128)])
    rooms = SelectField("Installed in", coerce=int)
    submit = SubmitField("Save changes")

from server.auth import bp as auth_bp
app.register_blueprint(auth_bp)#, url_prefix='/auth')


# User Login & Registration

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# UI

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/setup-cameras", methods=["GET", "POST"])
@login_required
def setup_cameras():
    camera_form = CameraForm()
    rooms = Room.query.all()
    camera_form.rooms.choices = [(room.id, room.name) for room in rooms]

    if camera_form.validate_on_submit():
        new_cam = Camera(url=camera_form.url.data, username=camera_form.username.data, password=camera_form.password.data)
        room = Room.query.get(camera_form.rooms.data)
        room.cameras.append(new_cam)
        db.session.commit()
        flash("Added camera with url {}".format(camera_form.url.data))
        return redirect(url_for('setup_cameras'))

    cameras = Camera.query.all()
    return render_template("setup-cameras.html", cameras=cameras, rooms=rooms, camera_form=camera_form, mode="setup")


@app.route("/setup-cameras/edit-camera/<int:cam_id>", methods=["GET", "POST"])
@login_required
def edit_camera(cam_id):
    cam = Camera.query.get(cam_id)
    camera_data = {"url": cam.url, "username": cam.username, "password": cam.password, "rooms": cam.room_id}
    camera_form = CameraForm(data=camera_data)
    rooms = Room.query.all()
    camera_form.rooms.choices = [(room.id, room.name) for room in rooms]

    if camera_form.validate_on_submit():
        cam.url = camera_form.url.data
        cam.username = camera_form.username.data
        cam.password = camera_form.password.data
        cam.room_id = camera_form.rooms.data
        db.session.commit()
        flash("Updated camera {}".format(cam.id))
        return redirect(url_for('setup_cameras'))

    cameras = Camera.query.all()
    return render_template("setup-cameras.html", cameras=cameras, rooms=rooms, camera_form=camera_form, mode="edit")


@app.route("/setup-cameras/remove-camera/<int:cam_id>", methods=["GET", "POST"])
@login_required
def remove_camera(cam_id):
    cam = Camera.query.get(cam_id)
    if request.method == "POST":
        db.session.delete(cam)
        db.session.commit()
        flash("Sucessfully removed camera {}".format(cam.id))
        return redirect(url_for('setup_cameras'))
    rooms = Room.query.all()
    cameras = Camera.query.all()
    return render_template("setup-cameras.html", cameras=cameras, rooms=rooms, mode="remove", cam_id=cam.id)


@app.route("/setup-rooms", methods=["GET", "POST"])
@login_required
def setup_rooms():
    room_form = RoomForm()
    if room_form.validate_on_submit():
        room = Room(name=room_form.name.data, description=room_form.description.data)
        db.session.add(room)
        db.session.commit()
        flash("Added room {}".format(room_form.name.data))
        return redirect(url_for('setup_rooms'))
    rooms = Room.query.all()
    return render_template("setup-rooms.html", rooms=rooms, room_form=room_form, mode="setup")


@app.route("/setup-rooms/edit-room/<int:room_id>", methods=["GET", "POST"])
@login_required
def edit_room(room_id):
    room = Room.query.get(room_id)
    room_data = {"name": room.name, "description": room.description}
    room_form = RoomForm(data=room_data)
    if room_form.validate_on_submit():
        room.name = room_form.name.data
        room.description = room_form.description.data
        db.session.commit()
        flash("Updated room {} (ID: {})".format(room_form.name.data, room.id))
        return redirect(url_for('setup_rooms'))
    rooms = Room.query.all()
    return render_template("setup-rooms.html", rooms=rooms, room_form=room_form, mode="edit")


@app.route("/setup-rooms/remove-room/<int:room_id>", methods=["GET", "POST"])
@login_required
def remove_room(room_id):
    room = Room.query.get(room_id)
    if request.method == "POST":
        db.session.delete(room)
        db.session.commit()
        flash("Sucessfully removed {} (ID: {})".format(room.name, room.id))
        return redirect(url_for('setup_rooms'))
    rooms = Room.query.all()
    return render_template("setup-rooms.html", rooms=rooms, mode="remove", room_id=room.id, room_name=room.name)


@app.route("/setup-general")
@login_required
def setup_general():
    return render_template("setup-general.html")


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
