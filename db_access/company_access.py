from flask_login import current_user

from models import Company
from app import db

from db_access.decorator_access import \
    check_role_and_relationship_to_corporation

current_user_id = current_user.id


@check_role_and_relationship_to_corporation(role_id=999)
def create_company(corporation_id, name_company, about_company):
    company = Company(creator_user_id=current_user_id,
                      name=name_company,
                      about=about_company,
                      corporation_id=corporation_id)

    db.session.add(company)
    db.session.commit()
    return company


def company_by_slug(company_slug):
    company = Company.query.filter_by(slug=company_slug).first()
    return company


def company_by_id(company_id):
    company = Company.query.filter_by(id=company_id).first()
    return company
