from uuid import uuid4

from app import db

from models.base import BaseModel


# !!!The order of inheritance from classes is important for the ability to
# override the method __init__!!! db.Model, BaseModel
class GroupClientPlaces(db.Model, BaseModel):
    slug_link = db.Column(db.String(128), index=True, unique=True)

    name = db.Column(db.String(64))
    about = db.Column(db.String(140))

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    # todo replace groups with group
    client_places = db.relationship(
        'ClientPlace', backref='group_client_places', lazy='dynamic')

    call_out = db.relationship(
        'CallOut', backref='group_client_places', lazy='dynamic')


    def __init__(self, *args, **kwargs):
        super(GroupClientPlaces, self).__init__(*args, **kwargs)
        self.slug = uuid4().hex
        self.slug_link = uuid4().hex

    def __repr__(self):
        return '<group of client places: {}>'. \
            format(self.name)