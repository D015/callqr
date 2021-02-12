from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     TextAreaField,
                     SelectField)

from wtforms.validators import (DataRequired,
                                ValidationError,
                                Email, Length)

from db_access import AdminAccess


class AdminForm(FlaskForm):
    email_admin = StringField('Email', validators=[DataRequired(), Email()])
    role_admin = SelectField('Role', validate_choice=False)

    submit_admin = SubmitField('Submit')
    cancel_admin = SubmitField('Cancel')

    def __init__(self, roles_to_choose, corporation_id, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        self.role_admin.choices = roles_to_choose
        self.corporation_id = corporation_id

    def validate_email_admin(self, email_admin):
        admins = AdminAccess(corporation_id=self.corporation_id,
                             email=email_admin.data.strip()). \
            admins_in_corporation_by_email()

        if admins is not None:
            raise ValidationError('Please use a different Email.')


class EditAdminForm(FlaskForm):
    about = TextAreaField('About admin',
                          validators=[Length(min=0, max=140)])
    phone = StringField('Enter phone number')
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', validate_choice=False)

    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, roles_to_choose, admin, *args, **kwargs):
        super(EditAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = roles_to_choose
        self.admin = admin

    def validate_email(self, email):
        if email.data.strip().lower() != self.admin.email.lower():
            admins = AdminAccess(corporation_id=self.admin.corporation_id,
                                 email=email.data.strip()). \
                admins_in_corporation_by_email()

            if admins is not None:
                raise ValidationError('Please use a different Email.')

    def validate_phone(self, phone):

        if phone.data is not None and phone.data.strip() != '' \
                and phone.data.strip().isdigit() is False:
            raise ValidationError('Use only digits')

        if phone.data.strip().isdigit() is True \
                and int(phone.data.strip()) != self.admin.phone:

            admins = AdminAccess(corporation_id=self.admin.corporation_id,
                                 phone=phone.data.strip()). \
                admins_in_corporation_by_phone()

            if admins is not None:
                raise ValidationError('Please use a different Phone.')
