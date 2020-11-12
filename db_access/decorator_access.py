from flask_login import current_user
from models import Admin, Employee, Company


def check_role_and_relationship_to_corporation(role_id=0):
    def decorator_admin(func):
        def check_func(corporation_id, *args, **kwargs):
            admin = current_user.admins.filter(
                Admin.corporation_id == corporation_id,
                Admin.role_id < role_id).first()
            if admin:
                return func(*args, **kwargs)
            else:
                pass
        return check_func
    return decorator_admin


def check_role_and_relationship_to_company(role_id=0):
    def decorator_employee(func):
        def check_func(company_id, *args, **kwargs):
            employee = current_user.employees.filter(
                Employee.company_id == company_id,
                Employee.role_id < role_id).first()

            if employee:
                return func(*args, **kwargs)

            else:
                admin = current_user.admins.filter_by(
                    corporation_id=(Company.query.filter(id=company_id).
                                    first()).corporation_id).first()
                if admin:
                    return func(*args, **kwargs)

                else:
                    pass

            return check_func
    return decorator_employee
