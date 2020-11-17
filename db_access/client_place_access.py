from flask_login import current_user

from models import ClientPlace
from app import db

from db_access.decorator_access import \
    check_role_and_relationship_to_company


@check_role_and_relationship_to_company(role_employee_id=999)
def create_client_place(company_id, name_client_place,
                        group_client_places_id=None):
    client_place = ClientPlace(
        creator_user_id=current_user.id, name=name_client_place,
        company_id=company_id, group_client_places_id=group_client_places_id)

    db.session.add(client_place)
    db.session.commit()
    return client_place
