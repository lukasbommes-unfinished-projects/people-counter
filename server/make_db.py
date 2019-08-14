import datetime
import random
from server import db
from server import User, Room, Camera, Count

# db.create_all()
#
# admin = User(username='admin', email='admin@example.com')
# guest = User(username='guest', email='guest@example.com')
#
# db.session.add(admin)
# db.session.add(guest)
# db.session.commit()
#
# room0 = Room(name="Dining Hall", description="Dining hall on L3")
# room1 = Room(name="Hallway North", description="")
# room2 = Room(name="Hallway South", description="Temporary arrangement")
# room3 = Room(name="Entrance", description="")
#
# cam0 = Camera(url="rtsp:://123.sdp", username="user1", password="pw1")
# cam1 = Camera(url="rtsp:://456.sdp", username="user1", password="pw1")
#
# room0.cameras.append(cam0)
# room0.cameras.append(cam1)
#
# db.session.add(room0)
# db.session.add(room1)
# db.session.add(room2)
# db.session.add(room3)
# db.session.commit()
#
# print(room0.cameras)
# print(cam0.query.with_parent(room0).filter(Camera.id != 2).all())

for i in range(100):
    count = Count(timestamp=datetime.datetime.now(), people_count=random.random())
    cams = Camera.query.all()
    print(cams)
    i = random.choice(range(len(cams)))
    cams[i].counts.append(count)

db.session.commit()
