import sqlite3
import datetime
from statistics import mean, StatisticsError

class PeopleCounterDB:

    def __init__(self, db_file):
        self.db_file = db_file
        self.tables = [
            '''CREATE TABLE IF NOT EXISTS `cameras` (
            `cam_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `url` TEXT NOT NULL,
            `username` TEXT NOT NULL,
            `password` TEXT NOT NULL )''',
            ####
            '''CREATE TABLE IF NOT EXISTS `rooms` (
            `room_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `name` TEXT NOT NULL )''',
            ####
            '''CREATE TABLE IF NOT EXISTS `layouts` (
            `room_id` INTEGER NOT NULL,
            `cam_id` INTEGER NOT NULL,
            PRIMARY KEY(`cam_id`,`room_id`) )''',
            ####
            '''CREATE TABLE IF NOT EXISTS `counts` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `timestamp` TEXT NOT NULL,
            `cam_id` INTEGER NOT NULL,
            `people_count` INTEGER NOT NULL )'''
            ]
        self.create_tables()


    def create_tables(self):
        conn = sqlite3.connect(self.db_file)
        crs = conn.cursor()
        # make tables
        for table in self.tables:
            crs.execute(table)
        conn.commit()
        conn.close()


    def insert_camera(self, url, username, password):
        conn = sqlite3.connect(self.db_file)
        with conn:
            conn.execute("INSERT INTO `cameras` VALUES (?,?,?,?)", (None, url, username, password))
        conn.close()

    def insert_room(self, name):
        conn = sqlite3.connect(self.db_file)
        with conn:
            conn.execute("INSERT INTO `rooms` VALUES (?,?)", (None, name,))
        conn.close()

    def insert_layout(self, room_id, cam_id):
        conn = sqlite3.connect(self.db_file)
        try:
            with conn:
                conn.execute("INSERT INTO `layouts` VALUES (?,?)", (room_id, cam_id))
        except sqlite3.IntegrityError:
            print("Layout with room_id {} and cam_id {} already exists. Skipping insertion.".format(room_id, cam_id))
        conn.close()

    def insert_count(self, room_id, people_count):
        conn = sqlite3.connect(self.db_file)
        ts = datetime.datetime.now()
        with conn:
            conn.execute("INSERT INTO `counts` VALUES (?,?,?,?)", (None, ts, room_id, people_count))
        conn.close()

    def get_cameras(self):
        conn = sqlite3.connect(self.db_file)
        crs = conn.cursor()
        crs.execute("SELECT * FROM `cameras`")
        cameras = crs.fetchall()
        conn.close()
        return cameras

    def get_rooms(self):
        conn = sqlite3.connect(self.db_file)
        crs = conn.cursor()
        crs.execute("SELECT * FROM `rooms`")
        rooms = crs.fetchall()
        conn.close()
        return rooms

    def get_layouts(self):
        conn = sqlite3.connect(self.db_file)
        crs = conn.cursor()
        crs.execute("SELECT * FROM `layouts`")
        layouts = crs.fetchall()
        conn.close()
        return layouts

    def get_cameras_in_room(self, room_id):
        conn = sqlite3.connect(self.db_file)
        crs = conn.cursor()
        crs.execute("SELECT `cam_id` FROM `layouts` WHERE `room_id`=?", (room_id,))
        cameras = [camera[0] for camera in crs.fetchall()]
        conn.close()
        return cameras

    def get_count(self, cam_id, window=1):
        conn = sqlite3.connect(self.db_file)
        crs = conn.cursor()
        crs.execute("SELECT `people_count` FROM `counts` WHERE `cam_id`=? LIMIT ?", (cam_id, window))
        try:
            counts = mean([count[0] for count in crs.fetchall()])
        except StatisticsError:
            counts = 0
        conn.close()
        return counts


    ### FOR DEVELOPMENT ONLY
    def fill_tables(self):
        self.insert_camera("rtsp://123.sdp", "user", "pw1")
        self.insert_camera("rtsp://456.sdp", "user", "pw1")
        self.insert_camera("rtsp://789.sdp", "user", "pw1")
        self.insert_room("dining room")
        self.insert_room("entrance hall")
        self.insert_layout(0, 0)
        self.insert_layout(0, 1)
        self.insert_layout(1, 2)
        self.insert_count(0, 13)
        self.insert_count(0, 12)
        self.insert_count(0, 14)
        self.insert_count(0, 16)
        self.insert_count(0, 15)
        self.insert_count(0, 17)
        self.insert_count(1, 105)


# TESTING
if __name__ == "__main__":

    db = PeopleCounterDB("../main_test.db")

    db.insert_camera("rtsp://123.sdp", "user", "pw1")
    db.insert_camera("rtsp://456.sdp", "user", "pw1")
    db.insert_camera("rtsp://789.sdp", "user", "pw1")

    db.insert_room("dining room")
    db.insert_room("entrance hall")

    db.insert_layout(0, 0)
    db.insert_layout(0, 1)
    db.insert_layout(1, 2)

    db.insert_count(0, 13)
    db.insert_count(0, 12)
    db.insert_count(0, 14)
    db.insert_count(0, 16)
    db.insert_count(0, 15)
    db.insert_count(0, 17)
    db.insert_count(1, 105)

    print("Cameras in room 0: {}".format(db.get_cameras_in_room(0)))
    print("Count in camera 0: {}".format(db.get_count(0, window=20)))

    print(db.get_cameras())
    print(db.get_rooms())
    print(db.get_layouts())
