from app import db
from db_access import ClientPlaceAccess
from models import Employee


class CallAccess(object):
    def __init__(self, client_place_slug, type_call_out):
        self.type_call_out = type_call_out
        self.client_place_slug = client_place_slug

    def call_to_emloyees(self):
        client_place = \
            ClientPlaceAccess(slug=self.client_place_slug).object_by_slug()
        cln_plc_empoyees_email = \
            db.session.query(Employee.email).filter(use_email_for_call=True).all()
        grp_cln_plcs_employees = \
            client_place.group_client_places.employees.all()
        call_to_emloyees = set(cln_plc_empoyees + grp_cln_plcs_employees)
        call_to_emloyees = {'call_to_emloyees_email': call_to_emloyees_email}
        return call_to_emloyees_email,
