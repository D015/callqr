from flask_login import current_user

from app import db
from db_access.admin import AdminAccess
from db_access.base import BaseAccess
from models import Corporation


class CorporationAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, name=None, about=None):
        super().__init__(id, slug, _obj, model=Corporation)
        self.about = about
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
        corporation = Corporation.query.filter(
            Corporation.creator_user_id == current_user.id,
            Corporation.name.ilike(self.name)).first()
        return corporation