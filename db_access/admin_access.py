from models import Admin, User
from app import db


def create_creator_admin(creator_user_id, about, email, phone, user_id,
                         corporation_id):
    admin = Admin(creator_user_id=creator_user_id, active=True, about=about,
                  email=email, phone=phone, role_admin_id=999, user_id=user_id,
                  corporation_id=corporation_id)
    db.session.add(admin)
    return admin


def create_admin(creator_user_id, about, email, phone, role_admin_id,
                 corporation_id):
    admin = Admin(creator_user_id=creator_user_id, about=about, email=email,
                  phone=phone, role_admin_id=role_admin_id,
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
