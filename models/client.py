from app import db

from models.base import BaseModel


class Client(BaseModel, db.Model):
    about = db.Column(db.String(140))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))

    call_out = db.relationship('CallOut', backref='client', lazy='dynamic')


    def __repr__(self):
        return '<Client {} {}>'.format(self.id, self.corporation_id)