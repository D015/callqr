from app import db
from flask_login import current_user

from models import Admin


def check_role_and_relationship_admin_to_corporation():  # !!!
    return


def create_creator_admin(about, email, phone, corporation_id):
    user_id = current_user.id
    admin = Admin(active=True, about=about, email=email, phone=phone,
                  role_admin_id=1, user_id=user_id,
                  corporation_id=corporation_id)
    db.session.add(admin)
    return admin


def create_admin(about, email, phone, role_admin_id,
                 corporation_id):
    admin = Admin(about=about, email=email, phone=phone,
                  role_admin_id=role_admin_id,
                  corporation_id=corporation_id)
    db.session.add(admin)
    db.session.commit()
    return admin


def create_relationship_admin_to_user(admin_slug, user):
    admin = Admin.query.filter(
        Admin.slug == admin_slug, Admin.archived is False).first()
    user_admin_corporation = user.admins.filter_by(
        corporation_id=admin.corporation_id).first()
    if admin.user_id or user_admin_corporation \
            or user.archived or user.active is False:
        pass
    else:
        admin.id = user.id
        admin.active = True
        db.session.add(admin)
        db.session.commit()
        return admin
