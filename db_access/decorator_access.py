from flask import \
    flash, \
    redirect, \
    url_for

from flask_login import current_user

from db_access.company_access import company_by_slug
from db_access.corporation_access import corporation_by_slug

from models import Admin, Employee


def check_role_and_transform_corporation_slug_to_id(role_id=0):
    def decorator_admin(func):
        def check_admin(corporation_slug_or_id, *args, **kwargs):
            if type(corporation_slug_or_id) is not int:
                corporation_slug_or_id = \
                    corporation_by_slug(corporation_slug_or_id).id

            admin = current_user.admins.filter(
                Admin.corporation_id == corporation_slug_or_id,
                Admin.active == True, Admin.archived == False,
                Admin.role_id < role_id).first()

            if admin:
                return func(corporation_slug_or_id, *args, **kwargs)
            else:
                flash('Contact your administrator.')
                return redirect(url_for('index'))

        return check_admin

    return decorator_admin


def check_role_and_transform_all_slug_to_id(role_id=0):
    def decorator_employee(func):
        def check_employee(corporation_slug_or_id, company_slug_or_id,
                           *args, **kwargs):

            if type(company_slug_or_id) is not int:
                company_slug_or_id = company_by_slug(company_slug_or_id).id

            if type(corporation_slug_or_id) is not int:
                corporation_slug_or_id = \
                    corporation_by_slug(corporation_slug_or_id).id

            admin = current_user.admins.filter(
                Admin.corporation_id == corporation_slug_or_id,
                Admin.active == True, Admin.archived == False).first()

            if admin:
                return func(corporation_slug_or_id, company_slug_or_id,
                            *args, **kwargs)
            else:
                employee = current_user.employees.filter(
                    Employee.company_id == company_slug_or_id,
                    Employee.active == True, Employee.archived == False,
                    Employee.role_id < role_id).first()

                if employee:
                    return func(corporation_slug_or_id, company_slug_or_id,
                                *args, **kwargs)
                else:
                    flash('Contact your administrator.')
                    return redirect(url_for('index'))

        return check_employee

    return decorator_employee
