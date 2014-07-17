from miridan import db


class Thing(db.Document):
    location = db.GeoPointField()
    name = db.StringField()
