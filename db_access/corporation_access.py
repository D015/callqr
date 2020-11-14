from models import Corporation
from app import db

from db_access.admin_access import create_creator_admin


def create_corporation(current_user_id, name_corporation, current_user_email):
    corporation = Corporation(creator_user_id=current_user_id,
                              name=name_corporation)
    # try:
    db.session.add(corporation)
    db.session.flush()
    admin = create_creator_admin(creator_user_id=current_user_id,
                                 corporation_id=corporation.id,
                                 current_user_email=current_user_email)
    db.session.commit()
    return corporation, admin
    # except:
    #     db.session.rollback()


def same_corporation_name_for_creator_user(user_id, name_corporation):
    corporation = Corporation.query.filter_by(
        creator_user_id=user_id, name=name_corporation).first()
    return corporation
