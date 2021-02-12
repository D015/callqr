from flask_login import current_user

from db_access.base import BaseAccess
from models import Employee, GroupClientPlaces, ClientPlace
from utils.utils_add import add_commit


class CompanyAccess(object):
    pass


class EmployeeAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, first_name=None,
                 last_name=None, role_id=None,  about=None,
                 email=None, phone=None, telegram_chat_id=None,
                 corporation_id=None, company_id=None,
                 group_client_places_slug=None, group_client_places_id=None,
                 client_place_slug=None, client_place_id=None):
        super().__init__(id, slug, _obj, model=Employee)
        self.telegram_chat_id = telegram_chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.role_id = role_id
        self.email = email
        self.phone = phone
        self.about = about
        self.corporation_id = corporation_id
        self.company_id = company_id
        self.group_client_places_slug = group_client_places_slug
        self.group_client_places_id = group_client_places_id
        self.client_place_slug = client_place_slug
        self.client_place_id = client_place_id

    def create_employee(self):
        corporation_id = self.corporation_id \
            if self.corporation_id is not None \
            else CompanyAccess(id=self.id).object_by_id().corporation_id

        employee = Employee(creator_user_id=current_user.id, active=False,
                            first_name=self.first_name,
                            last_name=self.last_name,
                            about=self.about, email=self.email,
                            phone=self.phone, role_id=self.role_id,
                            corporation_id=corporation_id,
                            company_id=self.company_id)
        add_commit(employee)
        return employee

    def create_relationship_employee_to_user(self):
        employee = Employee.query.filter_by(
            slug=self.slug, active=False, archived=False, user_id=None,
            email=current_user.email).first()

        if employee and current_user.archived is False and current_user.active:
            current_user_employee_corporation = current_user.employees. \
                filter_by(corporation_id=employee.corporation_id).first()

            if current_user_employee_corporation is None:
                employee.user_id = current_user.id
                employee.active = True
                add_commit(employee)
                return employee
        return None

    def id_employee_of_current_user_by_company_id(self):
        employee = current_user.employees.filter_by(
            company_id=self.company_id).first()
        return employee.id if employee else None

    def employee_of_current_user_by_company_id(self):
        employee = current_user.employees.filter_by(
            company_id=self.company_id).first()
        return employee

    def employees_in_corporation_by_email(self):
        employees = Employee.query.filter(
            Employee.corporation_id == self.corporation_id,
            Employee.email.ilike(self.email)).first()
        return employees

    def employees_in_corporation_by_phone(self):
        employees = Employee.query.filter(
            Employee.corporation_id == self.corporation_id,
            Employee.phone == self.phone).first()
        return employees

    def employees_of_current_user(self):
        return current_user.employees.filter_by(active=True, archived=False)

    def employees_by_company_id(self):
        employees = Employee.query.filter_by(
            company_id=self.company_id).order_by(Employee.last_name.asc())
        return employees

    def employees_pending_of_current_user(self):
        employees_pending = Employee.query.filter_by(email=current_user.email,
                                                     active=False,
                                                     archived=False,
                                                     user_id=None)
        return employees_pending

    def groups_client_places_without_relationship_the_employee(self):
        groups_client_places = GroupClientPlaces.query.filter(
            GroupClientPlaces.company_id == self._obj.company_id,
            ~GroupClientPlaces.employees.contains(self._obj)).all()
        return groups_client_places

    def groups_client_places_with_relationship_the_employee(self):
        groups_client_places = self._obj.groups_client_places.all()
        return groups_client_places

    def client_places_without_relationship_the_employee(self):
        client_places = ClientPlace.query.filter(
            ClientPlace.company_id == self._obj.company_id,
            ~ClientPlace.employees.contains(self._obj)).all()
        return client_places

    def client_places_with_relationship_the_employee(self):
        client_places = self._obj.client_places.all()
        return client_places

    def add_telegram_chat_id(self):
        employee = Employee.query.filter_by(slug=self.slug).first()
        employee.telegram_chat_id = self.telegram_chat_id
        add_commit(employee)
        return True