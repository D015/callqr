from models import Corporation
from app import db
from functions.create_admin import create_add_admin


def create_corporation(name_corporation, about_corporation, about_admin,
                       email_admin, phone_admin, role_admin, user_id):
    corporation = Corporation(name=name_corporation, about=about_corporation)
    try:
        db.session.add(corporation)
        db.session.flush()
        create_add_admin(about=about_admin, email=email_admin,
                         phone=phone_admin, role=role_admin, user_id=user_id,
                         corporation_id=corporation.id)
        db.session.commit()
    except:
        db.session.rollback()
