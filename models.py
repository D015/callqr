from datetime import datetime
from uuid import uuid4

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
# import qrcode
import pyqrcode
import os.path

from app import app, db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def generate_token_slug():
    return uuid4().hex


user_client_place = db.Table('user_client_place',
                             db.Column('user_id', db.Integer,
                                       db.ForeignKey('user.id')),
                             db.Column('client_place_id', db.Integer,
                                       db.ForeignKey('client_place.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about = db.Column(db.String(140))
    password_hash = db.Column(db.String(128))
    slug = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    companys = db.relationship('Company', backref='creator', lazy='dynamic')

    client_places = db.relationship('ClientPlace', secondary=user_client_place,
                                    backref=db.backref('users', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    creator_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    client_places = db.relationship('ClientPlace',
                                    backref='company_client_place',
                                    lazy='dynamic')

    groups_client_places = db.relationship('GroupClientPlaces',
                                    backref='company_group_client_places',
                                    lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Company {}>'.format(self.name)


class GroupClientPlaces(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    slug = db.Column(db.String(128), index=True, unique=True)
    slug_link = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    client_places = db.relationship('ClientPlace',
                                    backref='group_client_places_client_place',
                                    lazy='dynamic')

    def qr_code(self):
        if self.slug_link:
            name_file = os.path.dirname(os.path.abspath(
                __file__)) + '/static/qr_codes/' + self.slug_link + '.'
            name_file_svg = name_file + 'svg'
            name_file_eps = name_file + 'eps'
            name_file_png = name_file + 'png'

            url = pyqrcode.create(
                'http://192.168.1.55:5005/callqr/{}'.format(self.slug_link),
                error='L', version=4)
            url.eps(name_file_eps, scale=4)
            url.svg(name_file_svg, scale=4)
            url.png(name_file_png, scale=4, module_color=[0, 0, 0, 255],
                    background=[0xff, 0xff, 0xff])
        return

    def __init__(self, *args, **kwargs):
        super(GroupClientPlaces, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()
        self.slug_link = generate_token_slug()
        self.qr_code()

    def __repr__(self):
        return '<group of client places: {}>'. \
            format(self.name)



class ClientPlace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    slug = db.Column(db.String(128), index=True, unique=True)
    slug_link = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    group_client_places_id = db.Column(db.Integer,
                                       db.ForeignKey('group_client_places.id'))

    def qr_code(self):
        if self.slug_link:
            name_file = os.path.dirname(os.path.abspath(
                __file__)) + '/static/qr_codes/' + self.slug_link + '.'
            name_file_svg = name_file + 'svg'
            name_file_eps = name_file + 'eps'
            name_file_png = name_file + 'png'

            url = pyqrcode.create(
                'http://192.168.1.55:5005/callqr/{}'.format(self.slug_link),
                error='L', version=4)
            url.eps(name_file_eps, scale=3)
            url.svg(name_file_svg, scale=3)
            url.png(name_file_png, scale=4, module_color=[0, 0, 0, 255],
                    background=[0xff, 0xff, 0xff])
        return

    def __init__(self, *args, **kwargs):
        super(ClientPlace, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()
        self.slug_link = generate_token_slug()
        self.qr_code()

    def __repr__(self):
        return '<client place {}>'.format(self.id)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)

    user_id = db.relationship("User", uselist=False,
                              backref='person_user')

    employee_id = db.relationship("Employee", uselist=False,
                                  backref='person_employee')

    client_id = db.relationship("Client", uselist=False,
                                backref='person_client')




    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Person {} {}>'.format(self.first_name, self.last_name)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))


    def __init__(self, *args, **kwargs):
        super(Employee, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Person {} {}>'.format(self.first_name, self.last_name)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))


    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

