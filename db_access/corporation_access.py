from flask_login import current_user

from models import Corporation
from app import db

from db_access.admin_access import create_creator_admin


def create_corporation(name_corporation):
    corporation = Corporation(creator_user_id=current_user.id,
                              name=name_corporation)
    # try:
    db.session.add(corporation)
    db.session.flush()
    admin = create_creator_admin(corporation_id=corporation.id)
    db.session.commit()
    return corporation, admin
    # except:
    #     db.session.rollback()


def same_corporation_name_for_creator_user(user_id, name_corporation):
    corporation = Corporation.query.filter_by(
        creator_user_id=user_id, name=name_corporation).first()
    return corporation


def corporation_by_slug(corporation_slug):
    corporation = Corporation.query.filter_by(slug=corporation_slug).first()
    return corporation


def company_by_id(corporation_id):
    corporation = Corporation.query.filter_by(id=corporation_id).first()
    return corporation
