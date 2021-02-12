from flask import render_template
from flask_login import current_user

from models import (Admin,
                    Client,
                    Employee)
from utils.utils_add import sort_dict_value

from .base import BaseAccess
from .company import CompanyAccess


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