from app import app
from flask import flash, redirect, url_for
from flask_login import current_user
from sqlalchemy import or_

from app import db
from models import User, Admin, Employee, employees_to_groups_client_places, \
    employees_to_client_places, Role, Corporation, Company, GroupClientPlaces, \
    ClientPlace, Client


def add_commit(db_obj):
    db.session.add(db_obj)
    db.session.commit()


class BaseAccess:

    def __init__(self, id=None, slug=None, _obj=None, model=None):

        self.id = id
        self.slug = slug
        self._obj = _obj
        self.model = model

    def edit_model_object(self):
        for key, value in self.__dict__.items():
            if key[0] == '_' \
                    or key == 'id' \
                    or key == 'password':
                continue
            if value:
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
        obj = self.model.query.filter_by(id=self.id).first()
        return obj

    def object_by_id_or_404(self):
        obj = self.model.query.filter_by(id=self.id).first_or_404()
        return obj


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
                db.session.add(admin)
                db.session.commit()

                return admin
        return None

    def admins_in_corporation_by_email(self):
        admins = Admin.query.filter(
            Admin.corporation_id == self.corporation_id,
            Admin.email.ilike(self.email)).first()
        return admins

    def admins_of_current_user(self):
        return current_user.admins.filter_by(active=True, archived=False). \
            order_by(Admin.role_id.asc(), Admin.id.asc())

    # def object_by_slug(self):
    #     admin = Admin.query.filter_by(slug=self.slug).first()
    #     return admin

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
    def __init__(self, id=None, slug=None, _obj=None, first_name=None, last_name=None,
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
            else CompanyAccess(id=self.id).company_by_id().corporation_id

        employee = Employee(creator_user_id=current_user.id, active=False,
                            first_name=self.first_name,
                            last_name=self.last_name,
                            about=self.about, email=self.email,
                            phone=self.phone, role_id=self.role_id,
                            corporation_id=corporation_id,
                            company_id=self.company_id)
        db.session.add(employee)
        db.session.commit()

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
                db.session.add(employee)
                db.session.commit()

                return employee
        return None

    def employees_in_corporation_by_email(self):
        employees = Employee.query.filter(
            Employee.corporation_id == self.corporation_id,
            Employee.email.ilike(self.email)).first()
        return employees

    def is_relationship_employee_to_group_client_places(self):
        employee = Employee.query.filter_by(id=self.id).first_or_404()

        is_relationship = employee.groups_client_places.filter(
            employees_to_groups_client_places.c.group_client_places_id == \
            self.group_client_places_id).count() > 0

        return is_relationship

    def is_relationship_employee_to_client_place(self):
        employee = Employee.query.filter_by(id=self.id).first_or_404()

        is_relationship = employee.client_places.filter(
            employees_to_client_places.c.client_place_id == \
            self.client_place_id).count() > 0

        return is_relationship

    def create_relationship_group_client_places_to_employee(self):
        group_client_places = GroupClientPlacesAccess(
            slug=self.group_client_places_slug).group_client_places_by_slug()

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=group_client_places.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_id=group_client_places.company_id). \
                first_or_404()

        if self.id is None:
            return None, 'employee not selected'

        is_relationship = self.is_relationship_employee_to_group_client_places(
            employee.id, group_client_places.id)

        if is_relationship is False:
            employee.groups_client_places.append(group_client_places)

            db.session.add(employee)
            db.session.commit()

            return True, 'The relationship with the group successfully created'

        elif is_relationship:
            return False, 'The relationship with the group already existed'

        else:
            return None, 'error'

    def create_relationship_client_place_to_employee(self):
        client_place = ClientPlaceAccess(slug=self.client_place_slug). \
            client_place_by_slug()

        if self.id is None:
            employee = current_user.employees.filter_by(
                company_id=client_place.company_id).first_or_404()

        elif self.id:
            employee = Employee.query.filter_by(
                id=self.id, company_id=client_place.company_id). \
                first_or_404()

        if self.id is None:
            return None, 'employee not selected'

        is_relationship = self.is_relationship_employee_to_client_place(
            employee.id, client_place.id)

        if is_relationship is False:
            employee.client_places.append(client_place)

            db.session.add(employee)
            db.session.commit()

            return True, 'The relationship with the place successfully created'

        elif is_relationship:
            return False, 'The relationship with the place already existed'

        else:
            return None, 'error'

    def employees_of_current_user(self):
        return current_user.employees.filter_by(active=True, archived=False)

    def employees_by_company_id(self):
        empoyees = Employee.query.filter_by(
            company_id=self.company_id).order_by(Employee.last_name.asc())
        return empoyees

    # def object_by_slug(self):
    #     employee = Employee.query.filter_by(slug=self.slug).first()
    #     return employee

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

        roles = Role.query.filter(or_(Role.code == 10, Role.code == 99),
                                  Role.id > role_id_creator_admin,
                                  Role.active == True, Role.archived == False). \
            order_by(Role.id.desc()).all()

        return roles

    def roles_available_to_create_employee(self):
        admin = current_user.admins.filter_by(
            corporation_id=self.corporation_id).first()
        if admin:
            roles = Role.query.filter(or_(Role.code == 20, Role.code == 99),
                                      Role.active == True,
                                      Role.archived == False). \
                order_by(Role.id.desc()).all()
        else:
            role_id_creator_employee = current_user.employees.filter_by(
                company_id=self.company_id).first().role_id

            roles = Role.query.filter(or_(Role.code == 10, Role.code == 99),
                                      Role.id > role_id_creator_employee,
                                      Role.active == True,
                                      Role.archived == False). \
                order_by(Role.id.desc()).all()

        return roles

    def role_by_id(self):
        role = Role.query.filter_by(id=self.id).first()
        return role


class CorporationAccess(BaseAccess):
    def __init__(self, id=None, slug=None, name=None):
        super().__init__()
        self.id = id
        self.slug = slug
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

    def corporation_by_slug(self):
        corporation = Corporation.query.filter_by(slug=self.slug).first()
        return corporation

    def corporation_by_id(self):
        corporation = Corporation.query.filter_by(id=self.id).first()
        return corporation


class CompanyAccess(BaseAccess):
    def __init__(self, id=None, slug=None, name=None, about=None,
                 corporation_id=None):
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name
        self.about = about
        self.corporation_id = corporation_id

    def create_company(self):
        company = Company(creator_user_id=current_user.id,
                          name=self.name,
                          about=self.about,
                          corporation_id=self.corporation_id)

        db.session.add(company)
        db.session.commit()
        return company

    def company_by_slug(self):
        company = Company.query.filter_by(slug=self.slug).first()
        return company

    def company_by_id(self):
        company = Company.query.filter_by(id=self.id).first()
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
    def __init__(self, id=None, slug=None, name=None, about=None,
                 company_id=None):
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name
        self.about = about
        self.company_id = company_id

    def create_group_client_places(self):
        group_client_places = GroupClientPlaces(creator_user_id=current_user.id,
                                                name=self.name,
                                                about=self.about,
                                                company_id=self.company_id)

        db.session.add(group_client_places)
        db.session.commit()

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

    def group_client_places_by_id(self):
        group_client_places = GroupClientPlaces.query. \
            filter_by(id=self.id).first()

        return group_client_places

    def group_client_places_by_slug(self):
        group_client_places = GroupClientPlaces.query.filter_by(
            slug=self.slug).first()

        return group_client_places


class ClientPlaceAccess(BaseAccess):
    def __init__(self, id=None, slug=None, name=None, company_id=None,
                 group_client_places_id=None):
        super().__init__()
        self.id = id
        self.slug = slug
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

        db.session.add(client_place)
        db.session.commit()
        return client_place

    def client_place_in_company_by_name(self):
        client_place = ClientPlace.query.filter(
            ClientPlace.company_id == self.company_id,
            ClientPlace.name.ilike(self.name)).first()

        return client_place

    def client_place_by_id(self):
        client_place = ClientPlace.query.filter_by(
            id=self.id).first()

        return client_place

    def client_place_by_slug(self):
        client_place = ClientPlace.query.filter_by(
            slug=self.slug).first()

        return client_place

    def client_places_by_company_id(self):
        client_places = ClientPlace.query.filter_by(
            company_id=self.company_id).order_by(ClientPlace.name.asc())
        return client_places


def check_role_and_transform_corporation_slug_to_id(role_id=0):
    def decorator_admin(func):
        def check_admin(corporation_slug_to_id, *args, **kwargs):
            corporation = CorporationAccess(
                slug=corporation_slug_to_id).corporation_by_slug()
            corporation_slug_to_id = corporation.id

            admin = current_user.admins.filter(
                Admin.corporation_id == corporation_slug_to_id,
                Admin.active == True, Admin.archived == False,
                Admin.role_id < role_id).first()

            if admin:
                return func(corporation_slug_to_id, *args, **kwargs)

            flash('Contact your administrator.')
            return redirect(url_for('index'))

        return check_admin

    return decorator_admin


def check_role_and_return_corporation_and_transform_slug_to_id(
        first_role_id=0, second_role_id=0):
    def decorator_admin(func):
        def check_admin(corporation_slug_to_id, *args, **kwargs):
            corporation = CorporationAccess(
                slug=corporation_slug_to_id).corporation_by_slug()

            corporation_slug_to_id = corporation.id

            admin_by_first_role = current_user.admins.filter(
                Admin.corporation_id == corporation_slug_to_id,
                Admin.active == True, Admin.archived == False,
                Admin.role_id < first_role_id).first()

            if admin_by_first_role:
                first_role = True
                return func(corporation_slug_to_id, corporation, first_role,
                            *args, **kwargs)

            admin = current_user.admins.filter_by(
                corporation_id=corporation_slug_to_id,
                active=True, archived=False).first()

            employee = current_user.employees.filter_by(
                corporation_id=corporation_slug_to_id,
                active=True, archived=False).first()

            if (admin and admin.role_id < second_role_id) \
                    or (employee and employee.role_id < second_role_id):
                first_role = False
                return func(corporation_slug_to_id, corporation, first_role,
                            *args, **kwargs)

            flash('Contact your administrator.')
            return redirect(url_for('index'))

        return check_admin

    return decorator_admin


def check_role_and_transform_all_slug_to_id(role_id=0):
    def decorator_employee(func):
        def check_employee(company_slug_to_id,
                           *args, **kwargs):

            company = CompanyAccess(slug=company_slug_to_id). \
                company_by_slug()
            company_slug_to_id = company.id

            corporation_id = company.corporation_id

            admin = current_user.admins.filter(
                Admin.corporation_id == corporation_id,
                Admin.active == True, Admin.archived == False).first()

            if admin:
                return func(company_slug_to_id, corporation_id,
                            *args, **kwargs)
            else:
                employee = current_user.employees.filter(
                    Employee.company_id == company_slug_to_id,
                    Employee.active == True, Employee.archived == False,
                    Employee.role_id < role_id).first()

                if employee:
                    return func(company_slug_to_id, corporation_id,
                                *args, **kwargs)
                else:
                    flash('Contact your administrator.')
                    return redirect(url_for('index'))

        return check_employee

    return decorator_employee


def check_role_and_return_company_transform_slug_to_id(role_id=0):
    def decorator_employee(func):
        def check_employee(company_slug_to_id, *args, **kwargs):

            company = CompanyAccess(slug=company_slug_to_id). \
                company_by_slug()

            company_slug_to_id = company.id

            corporation = CorporationAccess(id=company.corporation_id). \
                corporation_by_id()

            admin = current_user.admins.filter(
                Admin.corporation_id == corporation.id,
                Admin.active == True, Admin.archived == False).first()

            if admin:
                return func(company_slug_to_id, company, *args, **kwargs)
            else:
                employee = current_user.employees.filter(
                    Employee.company_id == company_slug_to_id,
                    Employee.active == True, Employee.archived == False,
                    Employee.role_id < role_id).first()

                if employee:
                    return func(company_slug_to_id, company, *args, **kwargs)

            flash('Contact your administrator.')
            return redirect(url_for('index'))

        return check_employee

    return decorator_employee


def check_role_and_return_admin_and_transform_slug_to_id(others=False):
    def decorator_admin(func):
        def check_admin(admin_slug_to_id, *args, **kwargs):
            current_admin = current_user.admins.filter(
                Admin.slug == admin_slug_to_id).first()
            if current_admin:
                return func(admin_slug_to_id=current_admin.id,
                            admin=current_admin, *args, **kwargs)

            elif others:
                the_admin = AdminAccess(
                    slug=admin_slug_to_id).object_by_slug()

                admin = current_user.admins.filter(
                    Admin.corporation_id == the_admin.corporation_id,
                    Admin.active == True, Admin.archived == False).first()

                if admin and (admin.role_id < the_admin.role_id):
                    return func(admin_slug_to_id=the_admin.id,
                                admin=the_admin, *args, **kwargs)

            flash('Contact your administrator.')
            return redirect(url_for('index'))

        return check_admin

    return decorator_admin
