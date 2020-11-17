from flask_login import current_user

from app import db
from models import Employee

from db_access.decorator_access import \
    check_role_and_relationship_to_corporation
from db_access.company_access import company_by_id


@check_role_and_relationship_to_corporation
def create_employee(company_id, first_name, last_name, about, email, phone,
                    role_id):
    company = company_by_id(company_id=company_id)
    employee = Employee(creator_user_id=current_user.id, first_name=first_name,
                        last_name=last_name, about=about, email=email,
                        phone=phone, role_id=role_id,
                        corporation_id=company.corporation_id,
                        company_id=company_id)
    db.session.add(employee)
    db.session.commit()
    return employee


def create_relationship_employee_to_user(employee_slug, user):
    employee = Employee.query.filter(
        Employee.slug == employee_slug, Employee.archived is False).first()
    user_employee_corporation = user.employees.filter_by(
        corporation_id=employee.corporation_id).first()
    if employee.user_id or user_employee_corporation \
            or user.archived or user.active is False:
        pass
    else:
        employee.id = user.id
        employee.active = True
        db.session.add(employee)
        db.session.commit()
        return employee


def employees_in_corporation_by_email(corporation_id, email):
    employees = Employee.query.filter_by(corporation_id=corporation_id,
                                      email=email).first()
    return employees
