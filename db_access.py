from flask import flash, redirect, url_for, render_template
from flask_login import current_user
from sqlalchemy import or_

from app import db
from models import User, Admin, Employee, employees_to_groups_client_places, \
    employees_to_client_places, Role, Corporation, Company, GroupClientPlaces, \
    ClientPlace, Client
from utils_add import add_commit, sort_dict_value


class BaseAccess:

    def __init__(self, id=None, slug=None, _obj=None, model=None):
        self.id = id
        self.slug = slug
        self._obj = _obj
        self.model = model

    def object_is_exist(self):
        is_exist = self._obj.__class__.query.get(self._obj.id)
        return True if is_exist else False

    def remove_object(self):
        db.session.delete(self._obj)
        db.session.commit()

    def edit_model_object(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self._obj, key, value)
        add_commit(self._obj)
        return self._obj

    def object_by_slug(self):
        obj = self.model.query.filter_by(slug=self.slug).first()
        return obj

    def object_by_slug_or_404(self):
        obj = self.model.query.filter_by(slug=self.slug).first_or_404()
        return obj

    def object_by_id(self):
        obj = self.model.query.get(self.id)
        return obj

    def object_by_id_or_404(self):
        obj = self.model.query.filter_by(id=self.id).first_or_404()
        return obj

    def object_from_entire_db_by_slug(self):
        for model_i in db.Model._decl_class_registry.values():
            if hasattr(model_i, 'slug'):
                obj_i = model_i.query.filter_by(slug=self.slug).first()
                if obj_i:
                    return obj_i

class UserAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, username=None, email=None,
                 about=None, password=None):
        super().__init__(id, slug, _obj, model=User)

        self.username = username
        self.email = email
        self.password = password
        self.about = about

    def create_user(self):
        user = User(username=self.username, email=self.email)
        user.set_password(self.password)
        add_commit(user)
        return user

    def the_current_user(self):
        return current_user

    def the_current_user_of_model(self):
        user = User.query.filter_by(id=current_user.id).first_or_404()
        return user

    def users_by_email(self):
        users = User.query.filter(User.email.ilike(self.email)).first()
        return users

    def users_by_username(self):
        users = User.query.filter(User.username.ilike(self.username)).first()
        return users


class AdminAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, corporation_id=None,
                 email=None, role_id=None, about=None, phone=None):
        super().__init__(id, slug, _obj, model=Admin)
        self.corporation_id = corporation_id
        self.email = email
        self.role_id = role_id
        self.about = about
        self.phone = phone

    # TODO move 'first_role_id=!!!100!!!' to constants.py
    def create_creator_admin(self):
        admin = Admin(creator_user_id=current_user.id, active=True,
                      email=current_user.email, role_id=100,
                      user_id=current_user.id,
                      corporation_id=self.corporation_id)
        db.session.add(admin)
        return admin

    def create_admin(self):
        admin = Admin(creator_user_id=current_user.id, about=self.about,
                      email=self.email, phone=self.phone, role_id=self.role_id,
                      corporation_id=self.corporation_id, active=False)
        add_commit(admin)
        return admin

    def create_relationship_admin_to_user(self):

        admin = Admin.query.filter_by(
            slug=self.slug, active=False, archived=False, user_id=None,
            email=current_user.email).first()

        if admin and current_user.archived is False and current_user.active:
            current_user_admin_corporation = current_user.admins.filter_by(
                corporation_id=admin.corporation_id).first()

            if current_user_admin_corporation is None:
                admin.user_id = current_user.id
                admin.active = True
                add_commit(admin)
                return admin
        return None

    def admins_in_corporation_by_email(self):
        admins = Admin.query.filter(
            Admin.corporation_id == self.corporation_id,
            Admin.email.ilike(self.email)).first()
        return admins

    def admins_in_corporation_by_phone(self):
        admins = Admin.query.filter(
            Admin.corporation_id == self.corporation_id,
            Admin.phone == self.phone).first()
        return admins

    def admins_of_current_user(self):
        return current_user.admins.filter_by(active=True, archived=False). \
            order_by(Admin.role_id.asc(), Admin.id.asc())

    def admins_by_corporation_id(self):
        admins = Admin.query.filter_by(corporation_id=self.corporation_id). \
            order_by(Admin.role_id.desc(), Admin.id.asc())
        return admins

    def admins_pending_of_current_user(self):
        admins_pending = Admin.query.filter_by(email=current_user.email,
                                               active=False, archived=False,
                                               user_id=None)
        return admins_pending


class EmployeeAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, first_name=None,
                 last_name=None,
                 role_id=None, email=None, phone=None, about=None,
                 corporation_id=None, company_id=None,
                 group_client_places_slug=None, group_client_places_id=None,
                 client_place_slug=None, client_place_id=None):
        super().__init__(id, slug, _obj, model=Employee)
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
            current_user_employee_corporation = current_user.admins.filter_by(
                corporation_id=employee.corporation_id).first()

            if current_user_employee_corporation is None:
                employee.user_id = current_user.id
                employee.active = True
                add_commit(employee)
                return employee
        return None

    def id_employee_of_current_user(self):
        employee = current_user.employees.filter_by(
            company_id=self.company_id).first()
        return employee.id if employee else None

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

    def is_relationship_employee_to_group_client_places(self):
        employee = Employee.query.filter_by(id=self.id).first_or_404()

        is_relationship = employee.groups_client_places.filter(
            employees_to_groups_client_places.c.group_client_places_id == \
            self.group_client_places_id).count() > 0

        return is_relationship

    def is_relationship_employee_to_client_place(self):
        employee = Employee.query.filter_by(id=self.id).first()

        is_relationship = employee.client_places.filter(
            employees_to_client_places.c.client_place_id == \
            self.client_place_id).count() > 0

        return is_relationship

    def create_relationship_group_client_places_to_employee(self):
        group_client_places = GroupClientPlacesAccess(
            id=self.group_client_places_id).object_by_id()

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=group_client_places.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_id=group_client_places.company_id). \
                first_or_404()

        if employee is None:
            return None, 'employee not selected'

        self.id = employee.id

        is_relationship = self.is_relationship_employee_to_group_client_places()

        if is_relationship is False:
            employee.groups_client_places.append(group_client_places)

            add_commit(employee)
            return True, 'The relationship with the group successfully created'

        elif is_relationship:
            return False, 'The relationship with the group already existed'

        else:
            return None, 'error'

    def remove_relationship_group_client_places_to_employee(self):
        group_client_places = GroupClientPlacesAccess(
            id=self.group_client_places_id).object_by_id()

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=group_client_places.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_id=group_client_places.company_id). \
                first_or_404()

        if employee is None:
            return None, 'Employee not selected'

        self.id = employee.id

        is_relationship = self.is_relationship_employee_to_group_client_places()

        if is_relationship:
            employee.groups_client_places.remove(group_client_places)

            add_commit(employee)
            return True, 'The relationship with the group successfully removed'

        elif is_relationship:
            return False, 'There was no relationship with the group before'

        else:
            return None, 'error'

    def create_relationship_client_place_to_employee(self):
        client_place = ClientPlaceAccess(id=self.client_place_id). \
            object_by_id()

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=client_place.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_id=client_place.company_id). \
                first_or_404()

        if employee is None:
            return None, 'employee not selected'

        self.id = employee.id

        is_relationship = self.is_relationship_employee_to_client_place()

        if is_relationship is False:
            employee.client_places.append(client_place)

            add_commit(employee)
            return True, 'The relationship with the place successfully created'

        elif is_relationship:
            return False, 'The relationship with the place already existed'

        else:
            return None, 'error'

    def remove_relationship_client_place_to_employee(self):
        client_place = ClientPlaceAccess(
            id=self.client_place_id).object_by_id()

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=client_place.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_id=client_place.company_id). \
                first_or_404()

        if employee is None:
            return None, 'Employee not selected'

        self.id = employee.id

        is_relationship = self.is_relationship_employee_to_client_place()

        if is_relationship:
            employee.client_places.remove(client_place)

            add_commit(employee)
            return True, 'The relationship with the place successfully removed'

        elif is_relationship:
            return False, 'There was no relationship with the place before'

        else:
            return None, 'error'

    def employees_of_current_user(self):
        return current_user.employees.filter_by(active=True, archived=False)

    def employees_by_company_id(self):
        empoyees = Employee.query.filter_by(
            company_id=self.company_id).order_by(Employee.last_name.asc())
        return empoyees

    def employees_pending_of_current_user(self):
        employees_pending = Employee.query.filter_by(email=current_user.email,
                                                     active=False,
                                                     archived=False,
                                                     user_id=None)
        return employees_pending


class ClientAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None):
        super().__init__(id, slug, _obj, model=Client)

    def clients_of_current_user(self):
        return current_user.clients.filter_by(active=True, archived=False)


class RoleAccess:
    def __init__(self, id=None, corporation_id=None, company_id=None):

        self.id = id
        self.corporation_id = corporation_id
        self.company_id = company_id

    def roles_available_to_create_admin(self):
        role_id_creator_admin = current_user.admins.filter_by(
            corporation_id=self.corporation_id).first().role_id

        roles = Role.query.filter(or_(Role.code == 10, Role.code == 90),
                                  Role.id > role_id_creator_admin,
                                  Role.active == True, Role.archived == False). \
            order_by(Role.id.desc()).all()

        return roles

    def roles_available_to_create_employee(self):
        admin = current_user.admins.filter_by(
            corporation_id=self.corporation_id).first()
        if admin:
            roles = Role.query.filter(or_(Role.code == 20, Role.code == 90),
                                      Role.active == True,
                                      Role.archived == False). \
                order_by(Role.id.desc()).all()
        else:
            role_id_creator_employee = current_user.employees.filter_by(
                company_id=self.company_id).first().role_id

            roles = Role.query.filter(or_(Role.code == 10, Role.code == 90),
                                      Role.id > role_id_creator_employee,
                                      Role.active == True,
                                      Role.archived == False). \
                order_by(Role.id.desc()).all()

        return roles

    def role_by_id(self):
        role = Role.query.filter_by(id=self.id).first()
        return role


class CorporationAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, name=None, about=None):
        super().__init__(id, slug, _obj, model=Corporation)
        self.about = about
        self.name = name

    def create_corporation(self):
        corporation = Corporation(creator_user_id=current_user.id,
                                  name=self.name)
        # try:
        db.session.add(corporation)
        db.session.flush()
        admin = AdminAccess(corporation_id=corporation.id). \
            create_creator_admin()
        db.session.commit()
        return corporation, admin
        # except:
        #     db.session.rollback()

    def same_corporation_name_for_creator_user(self):
        corporation = Corporation.query.filter(
            Corporation.creator_user_id == current_user.id,
            Corporation.name.ilike(self.name)).first()
        return corporation


class CompanyAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, name=None, about=None,
                 corporation_id=None):
        super().__init__(id, slug, _obj, model=Company)
        self.name = name
        self.about = about
        self.corporation_id = corporation_id

    def create_company(self):
        company = Company(creator_user_id=current_user.id,
                          name=self.name,
                          about=self.about,
                          corporation_id=self.corporation_id)
        add_commit(company)
        return company

    def company_in_corporation_by_name(self):
        company = Company.query.filter(
            Company.corporation_id == self.corporation_id,
            Company.name.ilike(self.name)).first()
        return company

    def companies_by_corporation_id(self):
        companies = Company.query.filter_by(
            corporation_id=self.corporation_id, active=True, archived=False). \
            order_by(Company.name.asc())
        return companies

    def companies_of_current_user_by_corporation_id(self):
        # companies_of_corporation = companies_by_corporation_id(corporation_id)
        companies = Company.query.join(
            Admin, Company.corporation_id == Admin.corporation_id). \
            filter(Admin.user_id == current_user.id).all()
        return companies


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
            order_by(GroupClientPlaces.name.asc())
        return groups_client_places


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
            company_id=self.company_id).order_by(ClientPlace.name.asc())
        return client_places


def role_validation_object_return_transform_slug_to_id(myself=None,
                                                       another_id_limit=900,
                                                       **kwargs_decor):
    """ role_id: (role_id=300, role_id_1=500, ... role_id_n = 700)
    OR
     myself: (myself=True or myself=False),
     another_id_limit=701,
     id_diff:(id_diff_1=-300, id_diff_2=-200, id_diff_3=100 ) """

    def decorator_role(func):
        def check_role(**kwargs):

            slug_arg_name = None
            obj_slug = None

            # Getting the name of the argument and its value
            for arg_key, arg_value in kwargs.items():
                if '_slug_to_id' in arg_key:
                    slug_arg_name = arg_key
                    obj_slug = arg_value
                    break

            if slug_arg_name is None:
                return render_template('404.html')

            # Converting argument name to class-access name
            obj_name = slug_arg_name[:slug_arg_name.find('_slug')]
            obj_name_underscore_replaced_by_spaces = obj_name.replace('_', ' ')
            cls_name_with_spaces = \
                obj_name_underscore_replaced_by_spaces.title()
            cls_name = cls_name_with_spaces.replace(' ', '')
            cls_name_access = cls_name + 'Access'

            # Assigning the class-access to the variable
            cls = globals().get(cls_name_access)
            # class-access object creation
            obj = cls(slug=obj_slug).object_by_slug_or_404()

            obj_id = obj.id

            # Changing the slug in the argument of the decorated function
            # to the id of this object
            kwargs[slug_arg_name] = obj_id

            kwargs.update({obj_name: obj})

            company_id = None
            corporation_id = None

            # Getting company_id and corporation_id
            # depending on the object class
            if cls.__name__ == 'ClientAccess':
                corporation_id = obj.corporation_id
                if myself and current_user.clients.filter(
                        Client.id == obj_id,
                        Client.active == True,
                        Client.archived == False).first():
                    kwargs.update({'valid_myself': True})
                    return func(**kwargs)

            elif cls.__name__ == 'EmployeeAccess':
                company_id = obj.company_id
                corporation_id = obj.corporation_id
                if myself and current_user.employees.filter(
                        Employee.id == obj_id,
                        Employee.active == True,
                        Employee.archived == False).first():
                    kwargs.update({'valid_myself': True})
                    return func(**kwargs)

            elif cls.__name__ == 'AdminAccess':
                corporation_id = obj.corporation_id
                if myself and current_user.admins.filter(
                        Admin.id == obj_id,
                        Admin.active == True,
                        Admin.archived == False).first():
                    kwargs.update({'valid_myself': True})
                    return func(**kwargs)

            elif cls.__name__ == 'CorporationAccess':
                corporation_id = obj_id

            elif cls.__name__ == 'CompanyAccess':
                company_id = obj_id
                corporation_id = obj.corporation_id

            elif cls.__name__ == 'GroupClientPlacesAccess' \
                    or cls.__name__ == 'ClientPlaceAccess':
                company_id = obj.company_id
                corporation_id = CompanyAccess(
                    id=company_id).object_by_id().corporation_id

            kwargs.update({'company_id': company_id,
                           'corporation_id': corporation_id})

            # Checking the role of the current user
            # and choosing a path depending on the result of the check
            admin = current_user.admins.filter(
                Admin.corporation_id == corporation_id,
                Admin.active == True, Admin.archived == False).first()
            if admin:
                current_user_role = admin.role_id

            else:
                if cls.__name__ == 'ClientAccess' \
                        or cls.__name__ == 'CorporationAccess' \
                        or cls.__name__ == 'AdminAccess':
                    employee = current_user.employees.filter(
                        Employee.corporation_id == corporation_id,
                        Employee.active == True,
                        Employee.archived == False).first()
                else:
                    employee = current_user.employees.filter(
                        Employee.company_id == company_id,
                        Employee.active == True,
                        Employee.archived == False).first()
                if employee:
                    current_user_role = employee.role_id
                else:
                    return render_template('404.html')

            # Checking the role of the current user
            # and choosing a path depending on the result of the check

            for arg_decor_key, arg_decor_value in sort_dict_value(kwargs_decor):

                if myself is not None and 'id_diff' in arg_decor_key \
                        and current_user_role < another_id_limit \
                        and current_user_role \
                        <= obj.role_id + arg_decor_value:
                    kwargs.update({'valid_' + arg_decor_key: True})
                    return func(**kwargs)
                elif 'role_id' in arg_decor_key and \
                        current_user_role <= arg_decor_value:
                    kwargs.update({'valid_' + arg_decor_key: True})
                    return func(**kwargs)
                else:
                    kwargs.update({'valid_' + arg_decor_key: False})

            return render_template('404.html')

        return check_role

    return decorator_role
