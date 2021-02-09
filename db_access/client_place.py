from flask_login import current_user

from db_access.base import BaseAccess
from models import ClientPlace
from utils_add import add_commit


class ClientPlaceAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, name=None,
                 company_id=None,
                 group_client_places_id=None):
        super().__init__(id, slug, _obj, model=ClientPlace)
        self.name = name
        self.company_id = company_id
        self.group_client_places_id = group_client_places_id

    def create_client_place(self):

        if self.group_client_places_id.isdigit():
            client_place = ClientPlace(
                group_client_places_id=self.group_client_places_id,
                name=self.name, creator_user_id=current_user.id,
                company_id=self.company_id)
        else:
            client_place = ClientPlace(name=self.name,
                                       creator_user_id=current_user.id,
                                       company_id=self.company_id)

        add_commit(client_place)
        return client_place

    def client_place_in_company_by_name(self):
        client_place = ClientPlace.query.filter(
            ClientPlace.company_id == self.company_id,
            ClientPlace.name.ilike(self.name)).first()

        return client_place

    def client_places_by_company_id(self):
        client_places = ClientPlace.query.filter_by(
            company_id=self.company_id).order_by(ClientPlace.name.asc()).all()
        return client_places