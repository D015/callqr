from flask_login import current_user

from models import Corporation
from app import db

from db_access.admin_access import create_creator_admin

current_user_id = current_user.id


def create_corporation(name_corporation, about_corporation,
                       about_admin, email_admin, phone_admin):
    corporation = Corporation(creator_user_id=current_user_id,
                              name=name_corporation, about=about_corporation)
    try:
        db.session.add(corporation)
        db.session.flush()
        admin = create_creator_admin(about=about_admin, email=email_admin,
                                     phone=phone_admin,
                                     corporation_id=corporation.id)
        db.session.commit()
        return corporation, admin
    except:
        db.session.rollback()
