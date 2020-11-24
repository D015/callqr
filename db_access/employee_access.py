from flask_login import current_user

from app import db
from models import Employee

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


def create_by_yourself_relationship_to_client_place(client_place):
    employee = current_user.employees.filter_by(
        company_id=client_place.company_id).first_or_404()

    relationship = db.session.employees_to_client_places.query.filter(
        employee_id=employee.id, client_place_id=client_place.id).firstr()

    if relationship is None:
        employee.client_places.append(client_place)
        return True, 'successfully created'

    elif relationship:
        return False, 'has already been created'

    else:
        return None, 'error'


def create_by_yourself_relationship_to_groups_client_places(
        groups_client_places):

    employee = current_user.employees.filter_by(
        company_id=groups_client_places.company_id).first_or_404()

    relationship = db.session.employees_to_groups_client_places.query.filter(
        employee_id=employee.id,
        client_place_id=groups_client_places.id).firstr()

    if relationship is None:
        employee.groups_client_places.append(groups_client_places)
        return True, 'successfully created'

    elif relationship:
        return False, 'has already been created'

    else:
        return None, 'error'
