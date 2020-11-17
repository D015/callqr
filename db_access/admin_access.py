from flask_login import current_user

from app import db
from models import Admin

# from db_access.decorator_access import \
#     check_role_and_relationship_to_corporation


# TODO move 'role_id=!!!100!!!' to constants.py
def create_creator_admin(corporation_id):
    admin = Admin(creator_user_id=current_user.id, active=True,
                  email=current_user.email, role_id=100,
                  user_id=current_user.id, corporation_id=corporation_id)
    db.session.add(admin)
    return admin


# @check_role_and_relationship_to_corporation(role_id=401)
def create_admin(corporation_id, email, role_id, about=None, phone=None):
    admin = Admin(creator_user_id=current_user.id, about=about, email=email,
                  phone=phone, role_id=role_id,
                  corporation_id=corporation_id, active=False)
    db.session.add(admin)
    db.session.commit()
    return admin


def create_relationship_admin_to_user(admin_slug):
    admin = Admin.query.filter(
        Admin.slug == admin_slug, Admin.archived == False).first()

    user_admin_corporation = current_user.admins.filter_by(
        corporation_id=admin.corporation_id).first()

    if admin.user_id or user_admin_corporation \
            or current_user.archived or current_user.active is False:
        pass
    else:
        admin.id = current_user.id
        admin.active = True
        db.session.add(admin)
        db.session.commit()
        return admin


def admins_in_corporation_by_email(corporation_id, email):
    admins = Admin.query.filter_by(corporation_id=corporation_id, email=email).first()
    return admins
