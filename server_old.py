import json
from flask import Flask, jsonify, Response
from flask_httpauth import HTTPBasicAuth

from counter.database import PeopleCounterDB

app = Flask(__name__)
auth = HTTPBasicAuth()
db = PeopleCounterDB("main.db")
db.fill_tables() # FOR DEVELOPMENT ONLY!!!

@app.route("/")
def index():
    return "Welcome to people counter"

def _get_count(db, room_id):
    count = 0
    cam_ids = db.get_cameras_in_room(room_id)
    for cam_id in cam_ids:
         count += db.get_count(cam_id)
    return count

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
    app.run(host='0.0.0.0', debug=True)
