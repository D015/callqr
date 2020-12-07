from flask_login import current_user

from models import Corporation
from app import db

from db_access.admin_access import AdminAccess


class CorporationAccess:
    def __init__(self, id=None, slug=None, name=None):
        self.id = id
        self.slug = slug
        self.name = name

    def create_corporation(self):
        corporation = Corporation(creator_user_id=current_user.id,
                                  name=self.name)
        # try:
        db.session.add(corporation)
        db.session.flush()
        admin = AdminAccess(corporation_id=corporation.id). \
            create_creator_admin()
        db.session.commit()
        return corporation, admin
        # except:
        #     db.session.rollback()

    def same_corporation_name_for_creator_user(self):
        corporation = Corporation.query.filter_by(
            creator_user_id=current_user.id, name=self.name).first()
        return corporation

    def corporation_by_slug(self):
        corporation = Corporation.query.filter_by(slug=self.slug).first()
        return corporation

    def company_by_id(self):
        corporation = Corporation.query.filter_by(id=self.id).first()
        return corporation
