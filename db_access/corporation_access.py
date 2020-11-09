from models import Corporation
from app import db
from db_access.admin_access import create_add_admin


def create_corporation(creator_user_id, name_corporation, about_corporation,
                       about_admin, email_admin, phone_admin, user_id):
    corporation = Corporation(creator_user_id=creator_user_id,
                              name=name_corporation, about=about_corporation)
    try:
        db.session.add(corporation)
        db.session.flush()
        admin = create_add_admin(creator_user_id=creator_user_id,
                                 about=about_admin, email=email_admin,
                                 phone=phone_admin, role_admin_id='1',
                                 user_id=user_id, corporation_id=corporation.id)
        db.session.commit()
        return corporation, admin
    except:
        db.session.rollback()
