from app import db
from models import CallOut, CallIn
from utils.utils_add import add_commit


class CallAccess(object):
    def __init__(self, type_call_out_id=None, type_call_in_id=None,
                 destination=None, client_id=None, client_place_id=None,
                 group_client_places_id=None, company_id=None,
                 corporation_id=None, employee_id=None):
        self.type_call_out_id = type_call_out_id
        self.type_call_in_id = type_call_in_id
        self.destination = destination
        self.client_id = client_id
        self.client_place_id = client_place_id
        self.group_client_places_id = group_client_places_id
        self.company_id = company_id
        self.corporation_id = corporation_id
        self.employee_id = employee_id

    def create_call_of_employees_from_client_place(self):
        call_out = CallOut(corporation_id=self.corporation_id,
                           company_id=self.company_id,
                           group_client_places_id=self.group_client_places_id,
                           client_place_id=self.client_place_id,
                           client_id=self.client_id,
                           type_call_out_id=self.type_call_out_id)
        add_commit(call_out)
        call_in = CallIn(call_out_id=call_out.id,
                         employee_id=self.employee_id,
                         destination=self.destination,
                         type_call_in_id=self.type_call_in_id)
        add_commit(call_in)




