from flask_login import current_user

from app import db
from db_access.base import BaseAccess
from models import Admin
from utils_add import add_commit


class AdminAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, corporation_id=None,
                 email=None, role_id=None, about=None, phone=None):
        super().__init__(id, slug, _obj, model=Admin)
        self.corporation_id = corporation_id
        self.email = email
        self.role_id = role_id
        self.about = about
        self.phone = phone

    # TODO move 'first_role_id=!!!100!!!' to constants.py
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
        add_commit(admin)
        return admin

    def create_relationship_admin_to_user(self):

        admin = Admin.query.filter_by(
            slug=self.slug, active=False, archived=False, user_id=None,
            email=current_user.email).first()

        if admin and current_user.archived is False and current_user.active:
            current_user_admin_corporation = current_user.admins.filter_by(
                corporation_id=admin.corporation_id).first()

            if current_user_admin_corporation is None:
                admin.user_id = current_user.id
                admin.active = True
                add_commit(admin)
                return admin
        return None

    def admins_in_corporation_by_email(self):
        admins = Admin.query.filter(
            Admin.corporation_id == self.corporation_id,
            Admin.email.ilike(self.email)).first()
        return admins

    def admins_in_corporation_by_phone(self):
        admins = Admin.query.filter(
            Admin.corporation_id == self.corporation_id,
            Admin.phone == self.phone).first()
        return admins

    def admins_of_current_user(self):
        return current_user.admins.filter_by(active=True, archived=False). \
            order_by(Admin.role_id.asc(), Admin.id.asc())

    def admins_by_corporation_id(self):
        admins = Admin.query.filter_by(corporation_id=self.corporation_id). \
            order_by(Admin.role_id.desc(), Admin.id.asc())
        return admins

    def admins_pending_of_current_user(self):
        admins_pending = Admin.query.filter_by(email=current_user.email,
                                               active=False, archived=False,
                                               user_id=None)
        return admins_pending