from flask_login import current_user

from app import db
from models import Admin


class AdminAccess:
    def __init__(self, corporation_id=None, email=None, role_id=None,
                 slug=None, about=None, phone=None):
        self.corporation_id = corporation_id
        self.email = email
        self.role_id = role_id
        self.admin_slug = slug
        self.about = about
        self.phone = phone

    # TODO move 'role_id=!!!100!!!' to constants.py
    def create_creator_admin(self):
        admin = Admin(creator_user_id=current_user.id, active=True,
                      email=current_user.email, role_id=100,
                      user_id=current_user.id,
                      corporation_id=self.corporation_id)
        db.session.add(admin)
        return admin

    def create_admin(self):
        admin = Admin(creator_user_id=current_user.id, about=self.about,
                      email=self.email, phone=self.phone, role_id=self.role_id,
                      corporation_id=self.corporation_id, active=False)
        db.session.add(admin)
        db.session.commit()
        return admin

    def create_relationship_admin_to_user(self):

        admin = Admin.query.filter(
            Admin.slug == self.admin_slug, Admin.archived == False).first()

        user_admin_corporation = current_user.admins.filter_by(
            corporation_id=admin.corporation_id).first()

        if admin.user_id or user_admin_corporation \
                or current_user.archived or current_user.active is False:
            pass
        else:
            admin.user_id = current_user.id
            admin.active = True
            db.session.add(admin)
            db.session.commit()

            return admin

    def admins_in_corporation_by_email(self):
        admins = Admin.query.filter_by(corporation_id=self.corporation_id,
                                       email=self.email).first()
        return admins
