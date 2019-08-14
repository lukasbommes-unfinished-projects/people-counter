from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from server import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Room(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    cameras = db.relationship("Camera", cascade="save-update, delete", backref="room", lazy=True)

    def __repr__(self):
        return '<Room {}>'.format(self.name)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Camera(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    url = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    counts = db.relationship("Count", cascade="save-update, delete", backref="camera", lazy=True)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<Camera {}>'.format(self.url)


class Count(db.Model):
   id = db.Column(db.Integer, nullable=False, primary_key=True)
   timestamp = db.Column(db.DateTime, nullable=False)
   people_count = db.Column(db.Integer, nullable=False)
   cam_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)

   def to_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}

   def __repr__(self):
      return '<Count {}>'.format(self.id)
