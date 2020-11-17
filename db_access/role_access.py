from flask_login import current_user
from sqlalchemy import or_

from models import Role


def roles_available_to_create_admin(corporation_id):
    role_id_creator_admin = current_user.admins.filter_by(
        corporation_id=corporation_id).first().role_id

    roles = Role.query.filter(or_(Role.code == 10, Role.code == 99),
                              Role.id > role_id_creator_admin,
                              Role.active == True, Role.archived == False). \
        order_by(Role.id.desc()).all()
    # choices_roles = [(i.id, i.name) for i in roles]
    return roles
