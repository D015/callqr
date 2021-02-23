from app import db

from models.base import BaseModel


class CallOut(BaseModel, db.Model):
    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    group_client_places_id = db.Column(
        db.Integer, db.ForeignKey('group_client_places.id'))
    client_place_id = db.Column(db.Integer, db.ForeignKey('client_place.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    type_call_out_id = db.Column(db.Integer, db.ForeignKey('type_call_out.id'))

    call_in = db.relationship(
        'CallIn', backref='call_out', lazy='dynamic')

    def __repr__(self):
        return '<CallOut {}>'.format(self.id, self.corporation_id)

class CallIn(BaseModel, db.Model):
    call_out_id = db.Column(db.Integer, db.ForeignKey('call_out.id'))

    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    type_call_in_id = db.Column(db.Integer, db.ForeignKey('type_call_in.id'))

    def __repr__(self):
        return '<CallIn {}>'.format(self.id, self.corporation_id)


class TypeCallOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), default=True)
    archived = db.Column(db.Boolean(), default=False)

    code = db.Column(db.Integer, index=True, nullable=False)
    name = db.Column(db.String(120), index=True, nullable=False, unique=True)
    about = db.Column(db.String(120), index=True, unique=True)

    call_out = db.relationship(
        'CallOut', backref='type_call_out', lazy='dynamic')


class TypeCallIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), default=True)
    archived = db.Column(db.Boolean(), default=False)

    code = db.Column(db.Integer, index=True, nullable=False)
    name = db.Column(db.String(120), index=True, nullable=False, unique=True)
    about = db.Column(db.String(120), index=True, unique=True)

    call_in = db.relationship('CallIn', backref='type_call_in', lazy='dynamic')