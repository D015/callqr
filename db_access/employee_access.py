from flask_login import current_user

from app import db
from models import Employee

from db_access.decorator_access import \
    check_role_and_relationship_to_corporation

current_user_id = current_user.id


@check_role_and_relationship_to_corporation
def create_admin(company_id, first_name, last_name, about, email, phone,
                 role_id):
    admin = Employee(creator_user_id=current_user_id, about=about, email=email,
                  phone=phone, role_id=role_id,
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
