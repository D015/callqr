from flask_login import current_user

from models import GroupClientPlaces, Employee
from app import db


def create_group_client_places(company_id, name_group_client_places,
                               about_group_client_places=None):

    group_client_places = GroupClientPlaces(creator_user_id=current_user.id,
                                            name=name_group_client_places,
                                            about=about_group_client_places,
                                            company_id=company_id)

    db.session.add(group_client_places)
    db.session.commit()

    return group_client_places


def group_client_places_in_company_by_name(company_id, name):

    group_client_places = GroupClientPlaces.query.filter_by(
        company_id=company_id, name=name).first()

    return group_client_places


def groups_client_places_by_company_id(company_id):

    groups_client_places = GroupClientPlaces.query. \
            filter(GroupClientPlaces.company_id == company_id). \
            order_by(GroupClientPlaces.name.asc())

    return groups_client_places


def create_relationship_group_client_places_to_employee(
        employee_id, group_client_places_id):

    relationship = db.session.employees_to_groups_client_places.query.filter_by(
        employee_id=employee_id,
        groups_client_places_id=group_client_places_id).firstr()

    if relationship is None:
        group_client_places = GroupClientPlaces.query.filter_by(
            id=group_client_places_id).first_or_404()

        employee = Employee.query.filter_by(id=employee_id).first_or_404()

        group_client_places.employees.append(employee)

        return True, 'successfully created'

    elif relationship:
        return False, 'has already been created'

    else:
        return None, 'error'
