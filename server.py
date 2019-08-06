import os
import json
#from datetime import datetime

from flask import Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////peoplecounter/main.db'
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
    description = db.Column(db.Text, nullable=False)
    cameras = db.relationship("Camera", backref="room", lazy=True)

    def __repr__(self):
        return '<Room %r>' % self.name

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Camera(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    counts = db.relationship("Count", backref="camera", lazy=True)

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


# REST API

@app.route("/")
def index():
    return "Welcome to people counter"

@app.route("/people-counter/api/v1.0/rooms", methods=["GET"])
#@auth.login_required
def get_rooms():
    rooms = Room.query.all()
    return Response(json.dumps([room.to_dict() for room in rooms]),  mimetype='application/json')

@app.route("/people-counter/api/v1.0/rooms/<int:room_id>", methods=["GET"])
#@auth.login_required
def get_room(room_id):
    room = Room.query.get(room_id)
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
