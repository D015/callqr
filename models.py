from datetime import datetime
from uuid import uuid4

from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
# import qrcode
import pyqrcode
import os.path

from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


employees_to_groups_client_places = db.Table(
    'employees_to_groups_client_places',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('group_client_places_id', db.Integer, db.ForeignKey(
        'group_client_places.id')))

employees_to_client_places = db.Table(
    'employees_to_client_places',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('client_place_id', db.Integer, db.ForeignKey('client_place.id')))


class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    creator_user_id = db.Column(db.Integer)
    # todo slug - primary_key=True
    slug = db.Column(db.String(128), index=True, unique=True)
    active = db.Column(db.Boolean(), default=True)
    archived = db.Column(db.Boolean(), default=False)

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
        super(BaseModel, self).__init__(*args, **kwargs)
        self.slug = uuid4().hex
        self.creator_user_id = current_user.id


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


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), default=True)
    archived = db.Column(db.Boolean(), default=False)

    code = db.Column(db.Integer, index=True, nullable=False)
    name = db.Column(db.String(120), index=True, nullable=False, unique=True)
    about = db.Column(db.String(120), index=True, unique=True)

    admins = db.relationship('Admin', backref='role', lazy='dynamic')
    employees = db.relationship('Employee', backref='role', lazy='dynamic')


class Admin(BaseModel, db.Model):
    about = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.Integer, index=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'),
                               nullable=False)

    def __repr__(self):
        return '<Admin {} {}>'.format(self.email, self.id)


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


class Client(BaseModel, db.Model):
    about = db.Column(db.String(140))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    corporation_id = db.Column(db.Integer, db.ForeignKey('corporation.id'))

    call_out = db.relationship('CallOut', backref='client', lazy='dynamic')


    def __repr__(self):
        return '<Client {} {}>'.format(self.id, self.corporation_id)


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
        self.qr_code()

    def __repr__(self):
        return '<group of client places: {}>'. \
            format(self.name)


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
        self.qr_code()

    def __repr__(self):
        return '<client place {}>'.format(self.id)


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
