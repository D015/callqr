from app import db

from models.base import BaseModel


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