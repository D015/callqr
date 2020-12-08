from flask_login import current_user

from models import Company, Admin
from app import db

class CompanyAccess:
    def __init__(self, id=None, slug=None, name=None, about=None,
                 corporation_id=None):
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
        company = Company.query.filter_by(corporation_id=self.corporation_id,
                                          name=self.name).first()
        return company


    def companies_by_corporation_id(self):
        companies = Company.query.filter_by(
            corporation_id=self.corporation_id, active=True, archived=False).\
            order_by(Company.name.asc()).all()
        return companies


    def companies_of_current_user_by_corporation_id(self):
        # companies_of_corporation = companies_by_corporation_id(corporation_id)
        companies = Company.query.join(
            Admin, Company.corporation_id == Admin.corporation_id). \
            filter(Admin.user_id == current_user.id).all()
        return companies
