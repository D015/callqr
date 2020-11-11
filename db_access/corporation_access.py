from app import db

from models import Corporation

from access import create_creator_admin


def create_corporation(name_corporation, about_corporation,
                       about_admin, email_admin, phone_admin):
    corporation = Corporation(name=name_corporation, about=about_corporation)
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
