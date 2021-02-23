from app import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), default=True)
    archived = db.Column(db.Boolean(), default=False)

    code = db.Column(db.Integer, index=True, nullable=False)
    name = db.Column(db.String(120), index=True, nullable=False, unique=True)
    about = db.Column(db.String(120), index=True, unique=True)

    admins = db.relationship('Admin', backref='role', lazy='dynamic')
    employees = db.relationship('Employee', backref='role', lazy='dynamic')
