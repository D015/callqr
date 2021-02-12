from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     TextAreaField,
                     SelectField)

from wtforms.validators import (DataRequired,
                                ValidationError,
                                Email,
                                Length)

from db_access import EmployeeAccess
from forms import ActiveArchivedForm


class EmployeeForm(FlaskForm):
    first_name_employee = StringField('First name', validators=[DataRequired()])
    email_employee = StringField('Email', validators=[DataRequired(), Email()])
    role_employee = SelectField('Role', validate_choice=False)

    submit_employee = SubmitField('Submit')
    cancel_employee = SubmitField('Cancel')

    def __init__(self, roles_to_choose, corporation_id, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.role_employee.choices = roles_to_choose
        self.corporation_id = corporation_id

    def validate_email_employee(self, email_employee):
        employees = EmployeeAccess(corporation_id=self.corporation_id,
                                   email=email_employee.data.strip()). \
            employees_in_corporation_by_email()

        if employees is not None:
            raise ValidationError('Please use a different Email.')


# todo make the same size for all about fields
class EditEmployeeForm(ActiveArchivedForm, FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name')
    about = TextAreaField('About employee',
                          validators=[Length(min=0, max=140)])
    phone = StringField('Phone number')
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', validate_choice=False)

    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, roles_to_choose, employee, *args, **kwargs):
        super(EditEmployeeForm, self).__init__(*args, **kwargs)
        self.role.choices = roles_to_choose
        self.employee = employee

    def validate_email(self, email):
        if email.data.strip().lower() != self.employee.email.lower():
            employees = EmployeeAccess(
                corporation_id=self.employee.corporation_id,
                email=email.data.strip()).employees_in_corporation_by_email()

            if employees is not None:
                raise ValidationError('Please use a different Email.')

    def validate_phone(self, phone):

        if phone.data is not None and phone.data.strip() != '' \
                and phone.data.strip().isdigit() is False:
            raise ValidationError('Use only digits')

        if phone.data.strip().isdigit() is True \
                and int(phone.data.strip()) != self.employee.phone:

            employees = EmployeeAccess(
                corporation_id=self.employee.corporation_id,
                phone=phone.data.strip()).employees_in_corporation_by_phone()

            if employees is not None:
                raise ValidationError('Please use a different Phone.')

        # if phone.data is not None and phone.data.strip() != '' \
        #         and phone.data.strip().isdigit() is not True:
        #     raise ValidationError('Use only digits')
