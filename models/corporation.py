from app import db

from models.base import BaseModel

class Corporation(BaseModel, db.Model):
    name = db.Column(db.String(64))
    about = db.Column(db.String(140))

    admins = db.relationship(
        'Admin', cascade='all,delete', backref='corporation', lazy='dynamic')

    employees = db.relationship(
        'Employee', cascade='all,delete', backref='corporation', lazy='dynamic')

    clients = db.relationship(
        'Client', cascade='all,delete', backref='corporation', lazy='dynamic')

    companies = db.relationship(
        'Company', cascade='all,delete', backref='corporation', lazy='dynamic')

    call_out = db.relationship('CallOut', backref='corporation', lazy='dynamic')

    def __repr__(self):
        return '<Corporation {} {}>'.format(self.id, self.name)