from flask_login import current_user

from db_access.base import BaseAccess
from models import ClientPlace
from utils.utils_add import add_commit


class ClientPlaceAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, name=None,
                 company_id=None, group_client_places_id=None, slug_link=None):
        super().__init__(id, slug, _obj, model=ClientPlace)
        self.name = name
        self.company_id = company_id
        self.group_client_places_id = group_client_places_id
        self.slug_link = slug_link

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

    def selection_of_employee_contacts_to_call_from_client_place(self):
        client_place = \
            ClientPlaceAccess(slug_link=self.slug_link).object_by_slug()

        cln_plc_employees = client_place.employees. \
            filter_by(archived=False, active=True,
                      use_email_for_call=True).all()

        if client_place.group_client_places_id:
            grp_cln_plcs_employees = \
                client_place.group_client_places.employees. \
                    filter_by(archived=False, active=True,
                              use_email_for_call=True).all()
        else:
            grp_cln_plcs_employees = None
        employees = set(cln_plc_employees + grp_cln_plcs_employees)

        employees_emails = []
        employees_telegrams = []
        for employee in employees:
            if employee.use_email_for_call and employee.email:
                employees_emails.append((employee.id,
                                         employee.email))
            if employee.use_telegram_for_call and employee.elegram_chat_id:
                employees_telegrams.append((employee.id,
                                            employee.telegram_chat_id))

        cln_plc_empls_contacts = {'client_place': client_place,
                                  'employees_emails': employees_emails,
                                  'employees_telegrams': employees_telegrams}

        return cln_plc_empls_contacts
