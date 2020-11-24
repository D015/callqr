from flask_login import current_user

from models import ClientPlace
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


