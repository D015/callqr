from flask_login import current_user

from app import db
from db_access.client_place_access import client_place_by_id
from db_access.group_client_places_access import group_client_places_by_id
from models import Employee, \
    employees_to_groups_client_places, \
    employees_to_client_places

from db_access.company_access import company_by_id


def create_employee(company_id, first_name, email, role_id, last_name=None,
                    about=None, phone=None, corporation_id=None):
    if corporation_id is None:
        corporation_id = company_by_id(company_id=company_id).corporation_id

    employee = Employee(creator_user_id=current_user.id, first_name=first_name,
                        last_name=last_name, about=about, email=email,
                        phone=phone, role_id=role_id,
                        corporation_id=corporation_id,
                        company_id=company_id)
    db.session.add(employee)
    db.session.commit()

    return employee


def create_relationship_employee_to_user(employee_slug):
    employee = Employee.query.filter(
        Employee.slug == employee_slug, Employee.archived == False).first()

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


def employees_in_corporation_by_email(corporation_id, email):
    employees = Employee.query.filter_by(corporation_id=corporation_id,
                                         email=email).first()
    return employees


def is_relationship_employee_to_group_client_places(
        employee_id, group_client_places_id):
    employee = Employee.query.filter_by(id=employee_id).first_or_404()

    is_relationship = employee.groups_client_places.filter(
        employees_to_groups_client_places.c.group_client_places_id == \
        group_client_places_id).count() > 0

    return is_relationship


def is_relationship_employee_to_client_place(
        employee_id, client_place_id):
    employee = Employee.query.filter_by(id=employee_id).first_or_404()

    is_relationship = employee.client_places.filter(
        employees_to_client_places.c.client_place_id == \
        client_place_id).count() > 0

    return is_relationship


def create_relationship_group_client_places_to_employee(
        group_client_places_id, employee_id=0):
    group_client_places = group_client_places_by_id(group_client_places_id)

    if employee_id == 0:
        employee = current_user.employees.filter_by(
            company_id=group_client_places.company_id).first_or_404()

    elif employee_id:
        employee = Employee.query.filter_by(
            id=employee_id, company_1d=group_client_places.company_id). \
            first_or_404()

    elif employee_id is None:
        return None, 'employee not selected'

    is_relationship = is_relationship_employee_to_group_client_places(
        employee.id, group_client_places_id)

    if is_relationship is False:
        employee.groups_client_places.append(group_client_places)
        return True, 'successfully created'

    elif is_relationship:
        return False, 'has already been created'

    else:
        return None, 'error'


def create_relationship_client_place_to_employee(
        client_place_id, employee_id=0):
    client_place = client_place_by_id(client_place_id)

    if employee_id == 0:
        employee = current_user.employees.filter_by(
            company_id=client_place.company_id).first_or_404()

    elif employee_id:
        employee = Employee.query.filter_by(
            id=employee_id, company_1d=client_place.company_id). \
            first_or_404()

    elif employee_id is None:
        return None, 'employee not selected'

    is_relationship = is_relationship_employee_to_client_place(
        employee.id, client_place_id)

    if is_relationship is False:
        employee.client_places.append(client_place)
        return True, 'successfully created'

    elif is_relationship:
        return False, 'has already been created'

    else:
        return None, 'error'
