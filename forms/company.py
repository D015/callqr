from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     TextAreaField)

from wtforms.validators import (DataRequired,
                                ValidationError,
                                Length)

from db_access import CompanyAccess



class CompanyForm(FlaskForm):
    name_company = StringField('Enter name new company',
                               validators=[DataRequired()])
    submit_company = SubmitField('Submit')
    cancel_company = SubmitField('Cancel')

    def __init__(self, corporation_id, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.corporation_id = corporation_id

    def validate_name_company(self, name_company):
        company = CompanyAccess(corporation_id=self.corporation_id,
                                name=name_company.data.strip()). \
            company_in_corporation_by_name()

        if company is not None:
            raise ValidationError('Please use a different Company name.')


class EditCompanyForm(FlaskForm):
    name = StringField('Name company', validators=[DataRequired()])
    about = TextAreaField('About company', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, original_name_company, corporation_id, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)
        self.corporation_id = corporation_id
        self.original_name_company = original_name_company

    def validate_name(self, name):
        if name.data.strip().lower() != self.original_name_company.lower():
            company = CompanyAccess(corporation_id=self.corporation_id,
                                    name=name.data.strip()). \
                company_in_corporation_by_name()
            if company is not None:
                raise ValidationError('Please use a different Company name.')
