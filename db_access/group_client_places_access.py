from flask_login import current_user

from models import GroupClientPlaces
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
