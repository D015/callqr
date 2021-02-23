from app import db

from models.base import BaseModel

from models.many_to_many import (employees_to_groups_client_places,
                                 employees_to_client_places)



class Employee(BaseModel, db.Model):
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    about = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True)
    use_email_for_call = db.Column(db.Boolean(), default=False)
    telegram_chat_id = db.Column(db.String(64), index=True)
    use_telegram_for_call = db.Column(db.Boolean(), default=False)
    phone = db.Column(db.Integer, index=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    groups_client_places = db.relationship(
        'GroupClientPlaces', secondary=employees_to_groups_client_places,
        backref=db.backref('employees', lazy='dynamic'), lazy='dynamic')

    client_places = db.relationship(
        'ClientPlace', secondary=employees_to_client_places,
        backref=db.backref('employees', lazy='dynamic'), lazy='dynamic')

    call_in = db.relationship('CallIn', backref='employee', lazy='dynamic')

    def __repr__(self):
        return '<Employee {} {}>'.format(self.email, self.phone)
