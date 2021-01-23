from flask import flash, redirect, url_for, render_template
from flask_login import current_user
from sqlalchemy import or_, inspect

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
        if self._obj:
            obj_id = self._obj.id
            db.session.delete(self._obj)
            db.session.commit()
            return obj_id
        return None

    def edit_model_object(self, **kwargs):
        for key, value in kwargs.items():
            if value:
                setattr(self._obj, key, value)
            else:
                setattr(self._obj, key, None)
        add_commit(self._obj)
        return self._obj

    def object_by_slug(self):
        obj = self.model.query.filter_by(slug=self.slug).first()
        return obj

    def object_by_slug_or_404(self):
        obj = self.model.query.filter_by(slug=self.slug).first_or_404()
        return obj

    def object_id_by_slug(self):
        return self.object_by_slug().id

    def object_by_id(self):
        obj = self.model.query.get(self.id)
        return obj

    def object_by_id_or_404(self):
        obj = self.model.query.filter_by(id=self.id).first_or_404()
        return obj

    def slug_by_id(self):
        slug = self.model.query.get(self.id).slug
        return slug

    def object_from_entire_db_by_slug(self):
        for model_i in db.Model._decl_class_registry.values():
            if hasattr(model_i, 'slug'):
                obj_i = model_i.query.filter_by(slug=self.slug).first()
                if obj_i:
                    return obj_i


class BaseInspectAccess:
    def __init__(self, model_name=None, another_model_name=None):

        self.another_model_name = another_model_name
        self.model_name = model_name

    def backrefs_and_type_of_model_to_model(self):
        """ returns dictionary with keys:
        model_attr_another_model,
        another_model_attr_model,
        model_to_another_model_type.
        model_to_another_model_type is given in the format
        OneToMany, ManyToOne, ManyToMany"""

        relationship_model_to_another_model = {}

        model_mapper = inspect(globals()[self.model_name]).attrs

        for model_mapper_k, model_mapper_v in model_mapper.items():

            if type(model_mapper_v).__dict__['strategy_wildcard_key'] \
                    is 'relationship':

                model_mapper_v_dict = model_mapper_v.__dict__ \
                    if '__dict__' in dir(model_mapper_v) else None

                model_mapper_attr_entity = \
                    str(model_mapper_v_dict['entity']). \
                        replace('mapped class ', '').split('-')[0]

                if model_mapper_attr_entity == self.another_model_name:
                    another_model_attr_model = \
                        model_mapper_v_dict['back_populates']

                    model_attr_another_model = \
                        str(model_mapper_v_dict['_dependency_processor']). \
                            split('.')[1].replace(')', '')

                    model_to_model_type = \
                        str(model_mapper_v_dict['_dependency_processor']). \
                            split('DP(')[0]
                    relationship_model_to_another_model = {
                        'another_model_attr_model': another_model_attr_model,
                        'model_attr_another_model': model_attr_another_model,
                        'model_to_another_model_type': model_to_model_type
                    }


        return relationship_model_to_another_model


class BaseCompanyAccess(BaseAccess):
    def __init__(self, company_id=None, _obj=None, another_obj=None,
                 _obj_class_name=None, another_obj_class_name=None):

        self.company_id = company_id
        self._obj = _obj
        self._obj_class_name = _obj_class_name
        self.another_obj = another_obj
        self.another_obj_class_name = another_obj_class_name

    def objs_of_class_name_by_company_id(self):
        obj_class = globals()[self._obj_class_name]
        objs = obj_class.query.filter_by(company_id=self.company_id).all()
        return objs

    def is_relationship_obj_to_another_obj(self):
        if self._obj is None or self.another_obj is None:
            return render_template('404.html')

        inspect_obj_to_another_obj = BaseInspectAccess(
            model_name=self._obj.__class__.__name__,
            another_model_name=self.another_obj.__class__.__name__).\
            backrefs_and_type_of_model_to_model()

        _obj_attr_another_obj = inspect_obj_to_another_obj[
                                       'model_attr_another_model']

        _obj_another_obj = getattr(self._obj, _obj_attr_another_obj)

        is_iter = not(inspect_obj_to_another_obj[
                                       'model_to_another_model_type'] == \
                      'ManyToOne')
        if is_iter:
            is_relationship = self.another_obj in _obj_another_obj
        else:
            is_relationship = self.another_obj is _obj_another_obj

        relationship_info = {'is_relationship': is_relationship,
                             'is_iter': is_iter,
                             '_obj_attr_another_obj': _obj_attr_another_obj
        }

        return relationship_info

    def create_relationship_in_company_obj_to_another_obj(self):

        relationship_info = self.is_relationship_obj_to_another_obj()

        is_relationship = relationship_info['is_relationship']

        is_iter = relationship_info['is_iter']

        _obj_attr_another_obj = relationship_info['_obj_attr_another_obj']

        if is_relationship is False:
            if is_iter:
                getattr(self._obj, _obj_attr_another_obj).\
                    append(self.another_obj)
            else:
                setattr(self._obj, _obj_attr_another_obj, self.another_obj)

            add_commit(self._obj)
            return True, 'The relationship successfully created'
        elif is_relationship:
            return False, 'The relationship already existed'
        else:
            return None, 'error'

    def remove_relationship_obj_to_another_obj(self):
        relationship_info = self.is_relationship_obj_to_another_obj()

        is_relationship = relationship_info['is_relationship']

        is_iter = relationship_info['is_iter']

        _obj_attr_another_obj = relationship_info['_obj_attr_another_obj']

        if is_relationship:
            if is_iter:
                getattr(self._obj, _obj_attr_another_obj).\
                    remove(self.another_obj)
            else:
                setattr(self._obj, _obj_attr_another_obj, None)

            add_commit(self._obj)
            return True, 'The relationship successfully removed'
        elif is_relationship:
            return False, 'There was no relationship before'
        else:
            return None, 'error'
    # todo combine 'with' and 'without'
    #  to use another backrefs_and_type_of_model_to_model once
    def other_objs_without_relationship_obj(self):
        another_obj_class = globals()[self.another_obj_class_name]

        relationship_info = BaseInspectAccess(
            model_name=self._obj.__class__.__name__,
            another_model_name=self.another_obj_class_name).\
            backrefs_and_type_of_model_to_model()

        another_obj_class_attr_obj_name = \
            relationship_info['another_model_attr_model']

        relationship_type = relationship_info['model_to_another_model_type']

        if relationship_type == 'OneToMany':
            other_objs = another_obj_class.query.filter(
                another_obj_class.company_id == self._obj.company_id,
                getattr(another_obj_class,
                        another_obj_class_attr_obj_name) != self._obj).all()

        # (SQLAlchemy==1.3.17)SAWarning: Got None for value of column
        # client_place.group_client_places_id; this is unsupported for
        # a relationship comparison and will not currently produce
        # an IS comparison (but may in a future release)
        elif relationship_type == 'ManyToOne' \
                and getattr(self._obj,
                            relationship_info[
                                'model_attr_another_model']) is None:

            other_objs = another_obj_class.query.filter(
                another_obj_class.company_id == self._obj.company_id).all()

        else:
            other_objs = another_obj_class.query.filter(
                another_obj_class.company_id == self._obj.company_id,
                ~getattr(another_obj_class,
                         another_obj_class_attr_obj_name). \
                contains(self._obj)).all()

        return other_objs

    def other_objs_with_relationship_obj(self):
        relationship_info = BaseInspectAccess(
            model_name=self._obj.__class__.__name__,
            another_model_name=self.another_obj_class_name). \
            backrefs_and_type_of_model_to_model()

        _obj_other_objs = getattr(
            self._obj, relationship_info['model_attr_another_model'])

        # if many to one
        if relationship_info['model_to_another_model_type'] == 'ManyToOne':
            other_objs = [] if _obj_other_objs is None else [_obj_other_objs]
        else:
            other_objs = _obj_other_objs.all()

        return other_objs


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
            order_by(GroupClientPlaces.name.asc()).all()
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
            company_id=self.company_id).order_by(ClientPlace.name.asc()).all()
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
            obj = None
            obj_name = None
            cls_name = None

            # Getting the name of the argument and its value
            for arg_key, arg_value in kwargs.items():
                # if the name of the argument
                # contains the name of the object class
                if '_slug_to_id' in arg_key:
                    slug_arg_name = arg_key
                    obj_slug = arg_value

                    # Converting argument name to class-model
                    # and class-access name
                    obj_name = slug_arg_name[:slug_arg_name.find('_slug')]
                    obj_name_underscore_replaced_by_spaces = obj_name.replace(
                        '_', ' ')
                    cls_name_with_spaces = \
                        obj_name_underscore_replaced_by_spaces.title()
                    cls_name = cls_name_with_spaces.replace(' ', '')
                    cls_name_access = cls_name + 'Access'

                    # Assigning the class-access to the variable
                    cls = globals().get(cls_name_access)
                    # class-model object creation by class-access
                    obj = cls(slug=obj_slug).object_by_slug_or_404()
                    break
                # if there is no object class name
                # in the argument name
                elif 'slug' in arg_key:
                    slug_arg_name = arg_key
                    obj = BaseAccess(
                        slug=arg_value).object_from_entire_db_by_slug()
                    cls_name = obj.__class__.__name__
                    obj_name = cls_name.lower()
                    break

                # if the name of the argument does not have 'slug'
                else:
                    return render_template('404.html')

            obj_id = obj.id

            # Changing the slug in the argument of the decorated function
            # to the id of this object
            kwargs[slug_arg_name] = obj_id

            kwargs.update({obj_name: obj})

            company_id = None
            corporation_id = None

            # Getting company_id and corporation_id
            # depending on the object class
            if cls_name == 'Client':
                corporation_id = obj.corporation_id
                if myself and current_user.clients.filter(
                        Client.id == obj_id,
                        Client.active == True,
                        Client.archived == False).first():
                    kwargs.update({'valid_myself': True,
                                   'company_id': company_id,
                                   'corporation_id': corporation_id})
                    return func(**kwargs)

            elif cls_name == 'Employee':
                company_id = obj.company_id
                corporation_id = obj.corporation_id
                if myself and current_user.employees.filter(
                        Employee.id == obj_id,
                        Employee.active == True,
                        Employee.archived == False).first():
                    kwargs.update({'valid_myself': True,
                                   'company_id': company_id,
                                   'corporation_id': corporation_id})
                    return func(**kwargs)

            elif cls_name == 'Admin':
                corporation_id = obj.corporation_id
                if myself and current_user.admins.filter(
                        Admin.id == obj_id,
                        Admin.active == True,
                        Admin.archived == False).first():
                    kwargs.update({'valid_myself': True,
                                   'company_id': company_id,
                                   'corporation_id': corporation_id})
                    return func(**kwargs)

            elif cls_name == 'Corporation':
                corporation_id = obj_id

            elif cls_name == 'Company':
                company_id = obj_id
                corporation_id = obj.corporation_id

            elif cls_name == 'GroupClientPlaces' \
                    or cls_name == 'ClientPlace':
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
                if cls_name == 'Client' \
                        or cls_name == 'Corporation' \
                        or cls_name == 'Admin':
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
