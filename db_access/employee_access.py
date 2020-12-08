from flask_login import current_user

from app import db
from db_access.client_place_access import client_place_by_slug
from db_access.group_client_places_access import group_client_places_by_slug
from models import Employee, \
    employees_to_groups_client_places, \
    employees_to_client_places

from db_access.company_access import CompanyAccess


class EmployeeAccess:
    def __init__(self, id=None, slug=None, first_name=None, last_name=None,
                 role_id=None, email=None, phone=None, about=None,
                 corporation_id=None, company_id=None,
                 group_client_places_slug=None, group_client_places_id=None,
                 client_place_slug=None, client_place_id=None):
        self.id = id
        self.slug = slug
        self.first_name = first_name
        self.last_name = last_name
        self.role_id = role_id
        self.email = email
        self.phone = phone
        self.about = about
        self.corporation_id = corporation_id
        self.company_id = company_id
        self.group_client_places_slug = group_client_places_slug
        self.group_client_places_id = group_client_places_id
        self.client_place_slug = client_place_slug
        self.client_place_id = client_place_id

    def create_employee(self):
        corporation_id = self.corporation_id if self.corporation_id is None \
            else CompanyAccess(id=self.id).company_by_id().corporation_id

        employee = Employee(creator_user_id=current_user.id,
                            first_name=self.first_name,
                            last_name=self.last_name,
                            about=self.about, email=self.email,
                            phone=self.phone, role_id=self.role_id,
                            corporation_id=corporation_id,
                            company_id=self.id)
        db.session.add(employee)
        db.session.commit()

        return employee

    def create_relationship_employee_to_user(self):
        employee = Employee.query.filter(Employee.slug == self.slug,
                                         Employee.archived == False).first()

        user_employee_corporation = current_user.employees.filter_by(
            corporation_id=employee.corporation_id).first()

        if employee.user_id or user_employee_corporation \
                or current_user.archived or current_user.active is False:
            pass
        else:
            employee.user_id = current_user.id
            employee.active = True
            db.session.add(employee)
            db.session.commit()

            return employee

    def employees_in_corporation_by_email(self):
        employees = Employee.query.filter_by(corporation_id=self.corporation_id,
                                             email=self.email).first()
        return employees

    def is_relationship_employee_to_group_client_places(self):
        employee = Employee.query.filter_by(id=self.id).first_or_404()

        is_relationship = employee.groups_client_places.filter(
            employees_to_groups_client_places.c.group_client_places_id == \
            self.group_client_places_id).count() > 0

        return is_relationship

    def is_relationship_employee_to_client_place(self):
        employee = Employee.query.filter_by(id=self.id).first_or_404()

        is_relationship = employee.client_places.filter(
            employees_to_client_places.c.client_place_id == \
            self.client_place_id).count() > 0

        return is_relationship

    def create_relationship_group_client_places_to_employee(self):
        group_client_places = group_client_places_by_slug(
            self.group_client_places_slug)

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=group_client_places.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_1d=group_client_places.company_id). \
                first_or_404()

        if self.id is None:
            return None, 'employee not selected'

        is_relationship = self.is_relationship_employee_to_group_client_places(
            employee.id, group_client_places.id)

        if is_relationship is False:
            employee.groups_client_places.append(group_client_places)

            db.session.add(employee)
            db.session.commit()

            return True, 'The relationship with the group successfully created'

        elif is_relationship:
            return False, 'The relationship with the group already existed'

        else:
            return None, 'error'

    def create_relationship_client_place_to_employee(self):
        client_place = client_place_by_slug(self.client_place_slug)

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=client_place.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_1d=client_place.company_id). \
                first_or_404()

        if self.id is None:
            return None, 'employee not selected'

        is_relationship = self.is_relationship_employee_to_client_place(
            employee.id, client_place.id)

        if is_relationship is False:
            employee.client_places.append(client_place)

            db.session.add(employee)
            db.session.commit()

            return True, 'The relationship with the place successfully created'

        elif is_relationship:
            return False, 'The relationship with the place already existed'

        else:
            return None, 'error'
