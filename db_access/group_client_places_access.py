from flask_login import current_user

from models import GroupClientPlaces
from app import db

from db_access.decorator_access import \
    check_role_and_relationship_to_company

current_user_id = current_user.id


@check_role_and_relationship_to_company(role_employee_id=999)
def create_group_client_places(company_id, name_group_client_places,
                               about_group_client_places):
    group_client_places = GroupClientPlaces(creator_user_id=current_user_id,
                                            name=name_group_client_places,
                                            about=about_group_client_places,
                                            company_id=company_id)

    db.session.add(group_client_places)
    db.session.commit()
    return group_client_places
