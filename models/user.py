from uuid import uuid4

from flask_login import UserMixin
from werkzeug.security import (generate_password_hash,
                               check_password_hash)

from app import db, login

from models.base import BaseModel


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# !!!The order of inheritance from classes is important for the ability to
# override the method __init__!!! UserMixin, db.Model, BaseModel
class User(UserMixin, db.Model, BaseModel):
    creator_user_id = 0

    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    about = db.Column(db.String(140))

    admins = db.relationship('Admin', backref='user',
                             order_by="asc(Admin.role_id)",
                             lazy='dynamic')
    employees = db.relationship('Employee', backref='user',
                                order_by="asc(Employee.role_id)",
                                lazy='dynamic')
    clients = db.relationship('Client', backref='user', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.slug = uuid4().hex
        self.creator_user_id = 0

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
