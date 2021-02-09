from flask_login import current_user
from sqlalchemy import or_

from models import Role


class RoleAccess:
    def __init__(self, id=None, corporation_id=None, company_id=None):

        self.id = id
        self.corporation_id = corporation_id
        self.company_id = company_id

    def roles_available_to_create_admin(self):
        role_id_creator_admin = current_user.admins.filter_by(
            corporation_id=self.corporation_id).first().role_id

        roles = Role.query.filter(or_(Role.code == 10, Role.code == 90),
                                  Role.id > role_id_creator_admin,
                                  Role.active == True,
                                  Role.archived == False). \
            order_by(Role.id.desc()).all()

        return roles

    def roles_available_to_create_employee(self):
        admin = current_user.admins.filter_by(
            corporation_id=self.corporation_id).first()
        if admin:
            roles = Role.query.filter(or_(Role.code == 20, Role.code == 90),
                                      Role.active == True,
                                      Role.archived == False). \
                order_by(Role.id.desc()).all()
        else:
            role_id_creator_employee = current_user.employees.filter_by(
                company_id=self.company_id).first().role_id

            roles = Role.query.filter(or_(Role.code == 10, Role.code == 90),
                                      Role.id > role_id_creator_employee,
                                      Role.active == True,
                                      Role.archived == False). \
                order_by(Role.id.desc()).all()

        return roles

    def role_by_id(self):
        role = Role.query.filter_by(id=self.id).first()
        return role