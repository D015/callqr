from flask_login import current_user

from db_access.base import BaseAccess
from models import Company, Admin
from utils.utils_add import add_commit


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