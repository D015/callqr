from flask_login import current_user

from models import ClientPlace, Employee
from app import db


def create_client_place(company_id, name_client_place,
                        group_client_places_id=None):
    client_place = ClientPlace(
        creator_user_id=current_user.id, name=name_client_place,
        company_id=company_id, group_client_places_id=group_client_places_id)

    db.session.add(client_place)
    db.session.commit()
    return client_place


def client_place_in_company_by_name(company_id, name):
    client_place = ClientPlace.query.filter_by(
        company_id=company_id, name=name).first()

    return client_place


def create_relationship_client_place_to_employee(
        employee_id, client_place_id):

    relationship = employees_to_groups_client_places.c.query.filter_by(
        employee_id=employee_id,
        client_place_id=client_place_id).firstr()

    if relationship is None:
        client_place = ClientPlace.query.filter_by(
            id=client_place_id).first_or_404()

        employee = Employee.query.filter_by(id=employee_id).first_or_404()

        client_place.employees.append(employee)

        return True, 'successfully created'

    elif relationship:
        return False, 'has already been created'

    else:
        return None, 'error'
