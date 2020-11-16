from app import db
from models import Admin

from db_access.decorator_access import \
    check_role_and_relationship_to_corporation


def create_creator_admin(creator_user_id, corporation_id, current_user_email):
    admin = Admin(creator_user_id=creator_user_id, active=True,
                  email=current_user_email, role_id=100,
                  user_id=creator_user_id, corporation_id=corporation_id)
    db.session.add(admin)
    return admin


# @check_role_and_relationship_to_corporation
def create_admin(corporation_id, email, role_id, current_user_id,
                 about=None, phone=None):
    admin = Admin(creator_user_id=current_user_id, about=about, email=email,
                  phone=phone, role_id=role_id,
                  corporation_id=corporation_id, active=False)
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
