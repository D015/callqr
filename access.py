from app import db
from flask_login import current_user

from models import Admin


def check_role_and_relationship_to_where_used():  # !!!
    return


def is_active_and_is_not_archived(result_query):
    result_update_query = result_query.filter(
        active=True, archived=False).all()
    return result_update_query


class BaseAccess(object):
    def __init__(self, id=None, timestamp=None, creator_user_id=None, slug=None,
                 active=True, archived=False):
        self.id = id
        self.timestamp = timestamp
        self.creator_user_id = creator_user_id
        self.slug = slug
        self.active = active
        self.archived = archived


class AdminAccess(BaseAccess):
    def __init__(self, about=None, email=None, phone=None, role_admin_id=999,
                 user_id=None, corporation_id=None, *args, **kwargs):
        super(AdminAccess, self).__init__(*args, **kwargs)
        self.about = about
        self.email = email
        self.phone = phone
        self.role_admin_id = role_admin_id
        self.user_id = user_id
        self.corporation_id = corporation_id

    def create_creator_admin(self):
        self.user_id = current_user.id
        admin = Admin(about=self.about, email=self.email, phone=self.phone,
                      role_admin_id=self.role_admin_id, user_id=self.user_id,
                      corporation_id=self.corporation_id)
        db.session.add(admin)
        return admin

    def create_admin(self):
        admin = Admin(about=self.about, email=self.email, phone=self.phone,
                      role_admin_id=self.role_admin_id,
                      corporation_id=self.corporation_id)
        db.session.add(admin)
        db.session.commit()
        return admin

# !!!
    def create_relationship_admin_to_user(self, admin_slug=None, user=None):
        admin = Admin.query.filter_by(slug=admin_slug,
                                      active=True, archived=False).first()
        user_admin_corporation = user.admins.filter_by(
            corporation_id=admin.corporation_id).first()
        if admin.user_id or user_admin_corporation \
                or user.archived or user.active is False:
            pass
        else:
            admin.id = user.id
            admin.active = True
            db.session.add(admin)
            db.session.commit()
            return admin
