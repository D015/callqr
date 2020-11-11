from models import Corporation

from access import create_creator_admin


def create_corporation(creator_user_id, name_corporation, about_corporation,
                       about_admin, email_admin, phone_admin, user_id):
    corporation = Corporation(creator_user_id=creator_user_id,
                              name=name_corporation, about=about_corporation)
    try:
        db.session.add(corporation)
        db.session.flush()
        admin = create_creator_admin(creator_user_id=creator_user_id,
                                     about=about_admin, email=email_admin,
                                     phone=phone_admin, user_id=user_id,
                                     corporation_id=corporation.id)
        db.session.commit()
        return corporation, admin
    except:
        db.session.rollback()
