from app import db

from models.base import BaseModel


class Company(BaseModel, db.Model):
    name = db.Column(db.String(64))
    about = db.Column(db.String(140))

    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))

    employees = db.relationship(
        'Employee', backref='company', lazy='dynamic')

    client_places = db.relationship(
        'ClientPlace', cascade='all,delete', backref='company', lazy='dynamic')

    groups_client_places = db.relationship(
        'GroupClientPlaces', cascade='all,delete', backref='company',
        lazy='dynamic')

    call_out = db.relationship('CallOut', backref='company', lazy='dynamic')


    def __repr__(self):
        return '<Company {}>'.format(self.name)