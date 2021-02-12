from flask_login import current_user

from db_access.base import BaseAccess
from models import GroupClientPlaces
from utils.utils_add import add_commit


class GroupClientPlacesAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, name=None, about=None,
                 company_id=None):
        super().__init__(id, slug, _obj, model=GroupClientPlaces)
        self.name = name
        self.about = about
        self.company_id = company_id

    def create_group_client_places(self):
        group_client_places = GroupClientPlaces(creator_user_id=current_user.id,
                                                name=self.name,
                                                about=self.about,
                                                company_id=self.company_id)

        add_commit(group_client_places)
        return group_client_places

    def group_client_places_in_company_by_name(self):
        group_client_places = GroupClientPlaces.query.filter(
            GroupClientPlaces.company_id == self.company_id,
            GroupClientPlaces.name.ilike(self.name)).first()

        return group_client_places

    def groups_client_places_by_company_id(self):
        groups_client_places = GroupClientPlaces.query. \
            filter(GroupClientPlaces.company_id == self.company_id). \
            order_by(GroupClientPlaces.name.asc()).all()
        return groups_client_places