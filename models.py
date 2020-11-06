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


employees_to_groups_client_places = db.Table(
    'employees_to_groups_client_places',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('group_client_places_id', db.Integer, db.ForeignKey(
        'group_client_places.id')))

employees_to_client_places = db.Table(
    'employees_to_client_places',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('client_place_id', db.Integer, db.ForeignKey('client_place.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about = db.Column(db.String(140))
    password_hash = db.Column(db.String(128))
    slug = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    admins = db.relationship('Admin', backref='user', lazy='dynamic')
    employees = db.relationship('Employee', backref='user',
                               lazy='dynamic')
    clients = db.relationship('Client', backref='user', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(140))
    about = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number_telegram = db.Column(db.Integer, unique=True)
    slug = db.Column(db.String(128), index=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))

    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Admin {} {}>'.format(self.email, self.phone_number_telegram)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    role = db.Column(db.String(140))
    about = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number_telegram = db.Column(db.Integer, unique=True)
    slug = db.Column(db.String(128), index=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    groups_client_places = db.relationship(
        'GroupClientPlaces', secondary=employees_to_groups_client_places,
        backref=db.backref('employees', lazy='dynamic'), lazy='dynamic')

    client_places = db.relationship(
        'ClientPlace', secondary=employees_to_client_places,
        backref=db.backref('employees', lazy='dynamic'), lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Employee, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Employee {} {}>'.format(self.email, self.phone_number_telegram)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Client {} {}>'.format(self.id, self.corporation_id)


class Corporation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # creator_admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

    admins = db.relationship(
        'Admin', backref='corporation', lazy='dynamic')
    employees = db.relationship(
        'Employee', backref='corporation', lazy='dynamic')
    clients = db.relationship(
        'Client', backref='corporation', lazy='dynamic')
    companies = db.relationship(
        'Company', backref='corporation', lazy='dynamic')


    def __init__(self, *args, **kwargs):
        super(Corporation, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Corporation {} {}>'.format(self.id, self.name)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))

    employees = db.relationship(
        'Employee', backref='company', lazy='dynamic')
    client_places = db.relationship(
        'ClientPlace', backref='company', lazy='dynamic')
    groups_client_places = db.relationship(
        'GroupClientPlaces', backref='company', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.slug = generate_token_slug()

    def __repr__(self):
        return '<Company {}>'.format(self.name)


class GroupClientPlaces(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    about = db.Column(db.String(140))
    slug = db.Column(db.String(128), index=True, unique=True)
    slug_link = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    client_places = db.relationship(
        'ClientPlace', backref='group_client_places', lazy='dynamic')

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
    group_client_places_id = db.Column(
        db.Integer, db.ForeignKey('group_client_places.id'))

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