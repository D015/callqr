from app import db
from db_access import ClientPlaceAccess
from models import Employee


class CallAccess(object):
    def __init__(self, client_place_slug, type_call_out):
        self.type_call_out = type_call_out
        self.client_place_slug = client_place_slug

    def selection_of_employee_contacts_to_call_from_client_place(self):
        client_place = \
            ClientPlaceAccess(slug=self.client_place_slug).object_by_slug()
        cln_plc_employees = client_place.employees. \
            filter_by(archived=False, active=True,
                      use_email_for_call=True).all()

        grp_cln_plcs_employees = client_place.group_client_places.employees. \
            filter_by(archived=False, active=True,
                      use_email_for_call=True).all() \
            if client_place.group_client_places else None
        employees = set(cln_plc_employees + grp_cln_plcs_employees)

        emails = []
        telegrams = []
        for employee in employees:
            if employee.use_email_for_call:
                emails.append(employee.email)
            if employee.use_telegram_for_call:
                telegrams.append(employee.use_telegram_for_call)

        employee_contacts = {'emails': emails, 'telegrams': telegrams}
        return employee_contacts

    def call_of_employees_from_client_place(self):
        employee_contacts = \
            self.selection_of_employee_contacts_to_call_from_client_place()

