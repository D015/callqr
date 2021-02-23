from uuid import uuid4

from app import db

from models.base import BaseModel


# !!!The order of inheritance from classes is important for the ability to
# override the method __init__!!! db.Model, BaseModel
class ClientPlace(db.Model, BaseModel):
    slug_link = db.Column(db.String(128), index=True, unique=True)

    name = db.Column(db.String(64))

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    group_client_places_id = db.Column(
        db.Integer, db.ForeignKey('group_client_places.id'))

    call_out = db.relationship(
        'CallOut', backref='client_place', lazy='dynamic')


    def __init__(self, *args, **kwargs):
        super(ClientPlace, self).__init__(*args, **kwargs)
        self.slug = uuid4().hex
        self.slug_link = uuid4().hex

    def __repr__(self):
        return '<client place {}>'.format(self.id)