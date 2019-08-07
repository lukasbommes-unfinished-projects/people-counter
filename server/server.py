import os
import json
#from datetime import datetime

from flask import Flask, render_template, jsonify, Response, make_response, abort, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////peoplecounter/server/main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Database ORM

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# One room has many cameras
# One camera has many counts (at different times)

class Room(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cameras = db.relationship("Camera", cascade="save-update, delete", backref="room", lazy=True)

    def __repr__(self):
        return '<Room %r>' % self.name

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Camera(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    counts = db.relationship("Count", cascade="save-update, delete", backref="camera", lazy=True)

    def __repr__(self):
        return '<Camera %r>' % self.url

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Count(db.Model):
   id = db.Column(db.Integer, nullable=False, primary_key=True)
   timestamp = db.Column(db.DateTime, nullable=False)
   people_count = db.Column(db.Integer, nullable=False)
   cam_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)

   def __repr__(self):
      return '<Count %r>' % self.id

   def to_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# UI

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/setup-cameras", methods=["GET", "POST"])
def setup_cameras():
    if request.method == "POST":
        url = request.form.get("camera-url")
        auth_required = request.form.get("camera-auth-required")
        username = request.form.get("camera-username")
        password = request.form.get("camera-password")
        room_id = request.form.get("camera-room")
        print(url, auth_required, username, password, room_id)
        # check validity
        if not url:
            redirect(url_for('setup_cameras'))
        if auth_required and (not username or not password):
                redirect(url_for('setup_cameras'))
        # Todo: perform connectivity check and notify user about connectivity status
        # insert new camera into database
        if auth_required:
            new_cam = Camera(url=url, username=username, password=password)
        else:
            new_cam = Camera(url=url)
        # get the room and append camera to the room's camera list
        room = Room.query.get(room_id)
        room.cameras.append(new_cam)
        db.session.commit()
        return redirect(url_for('setup_cameras'))  # reload page

    rooms = Room.query.all()
    cameras = Camera.query.all()
    return render_template("setup-cameras.html", cameras=cameras, rooms=rooms)

@app.route("/setup-cameras/remove-camera-<int:cam_id>", methods=["POST"])
def remove_camera(cam_id):
    print("Removing cam {}".format(cam_id))
    cam = Camera.query.get(cam_id)
    db.session.delete(cam)
    db.session.commit()
    return redirect(url_for('setup_cameras'))

@app.route("/setup-rooms")
def setup_rooms():
    return render_template("setup-rooms.html")

@app.route("/setup-general")
def setup_general():
    return render_template("setup-general.html")


# REST API

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/people-counter/api/v1.0/rooms", methods=["GET"])
#@auth.login_required
def get_rooms():
    rooms = Room.query.all()
    if not rooms:
        abort(404)
    return Response(json.dumps([room.to_dict() for room in rooms]),  mimetype='application/json')


@app.route("/people-counter/api/v1.0/rooms/<int:room_id>", methods=["GET"])
#@auth.login_required
def get_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        abort(404)
    return Response(json.dumps(room.to_dict()),  mimetype='application/json')



@app.route("/people-counter/api/v1.0/counts", methods=["GET"])
@auth.login_required
def get_counts():
    counts = []
    room_ids = [room[0] for room in db.get_rooms()]
    for room_id in room_ids:
        count = _get_count(db, room_id)
        counts.append({"room_id": room_id, "people-count": count})
    return Response(json.dumps(counts),  mimetype='application/json')

@app.route("/people-counter/api/v1.0/counts/<int:room_id>", methods=["GET"])
@auth.login_required
def get_count(room_id):
    count = _get_count(db, room_id)
    return jsonify({"room_id": room_id, "people-count": count})

if __name__ == "__main__":
    if not os.path.exists('main.db'):
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
