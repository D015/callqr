from flask_login import current_user

from db_access.base import BaseAccess
from models import Client


class ClientAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None):
        super().__init__(id, slug, _obj, model=Client)

    def clients_of_current_user(self):
        return current_user.clients.filter_by(active=True, archived=False)