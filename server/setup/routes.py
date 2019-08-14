from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from server import db
from server.setup import bp
from server.setup.forms import CameraForm, RoomForm
from server.models import Room, Camera, Count


@bp.route("/setup-cameras", methods=["GET", "POST"])
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
        return redirect(url_for('setup.setup_cameras'))

    cameras = Camera.query.all()
    return render_template("setup/setup-cameras.html", cameras=cameras, rooms=rooms, camera_form=camera_form, mode="setup")


@bp.route("/setup-cameras/edit-camera/<int:cam_id>", methods=["GET", "POST"])
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
        return redirect(url_for('setup.setup_cameras'))

    cameras = Camera.query.all()
    return render_template("setup/setup-cameras.html", cameras=cameras, rooms=rooms, camera_form=camera_form, mode="edit")


@bp.route("/setup-cameras/remove-camera/<int:cam_id>", methods=["GET", "POST"])
@login_required
def remove_camera(cam_id):
    cam = Camera.query.get(cam_id)
    if request.method == "POST":
        db.session.delete(cam)
        db.session.commit()
        flash("Sucessfully removed camera {}".format(cam.id))
        return redirect(url_for('setup.setup_cameras'))
    rooms = Room.query.all()
    cameras = Camera.query.all()
    return render_template("setup/setup-cameras.html", cameras=cameras, rooms=rooms, mode="remove", cam_id=cam.id)


@bp.route("/setup-rooms", methods=["GET", "POST"])
@login_required
def setup_rooms():
    room_form = RoomForm()
    if room_form.validate_on_submit():
        room = Room(name=room_form.name.data, description=room_form.description.data)
        db.session.add(room)
        db.session.commit()
        flash("Added room {}".format(room_form.name.data))
        return redirect(url_for('setup.setup_rooms'))
    rooms = Room.query.all()
    return render_template("setup/setup-rooms.html", rooms=rooms, room_form=room_form, mode="setup")


@bp.route("/setup-rooms/edit-room/<int:room_id>", methods=["GET", "POST"])
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
        return redirect(url_for('setup.setup_rooms'))
    rooms = Room.query.all()
    return render_template("setup/setup-rooms.html", rooms=rooms, room_form=room_form, mode="edit")


@bp.route("/setup-rooms/remove-room/<int:room_id>", methods=["GET", "POST"])
@login_required
def remove_room(room_id):
    room = Room.query.get(room_id)
    if request.method == "POST":
        db.session.delete(room)
        db.session.commit()
        flash("Sucessfully removed {} (ID: {})".format(room.name, room.id))
        return redirect(url_for('setup.setup_rooms'))
    rooms = Room.query.all()
    return render_template("setup/setup-rooms.html", rooms=rooms, mode="remove", room_id=room.id, room_name=room.name)


@bp.route("/setup-general")
@login_required
def setup_general():
    return render_template("setup/setup-general.html")
