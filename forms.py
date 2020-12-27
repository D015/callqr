from flask_wtf import FlaskForm
from wtforms import SubmitField, \
    StringField, \
    PasswordField, \
    BooleanField, \
    TextAreaField, \
    SelectField, \
    RadioField, \
    SelectMultipleField, \
    widgets
from wtforms.validators import DataRequired, \
    ValidationError, \
    EqualTo, \
    Email, \
    Length, InputRequired
from flask_login import current_user

from models import User, \
    Company, \
    ClientPlace, \
    GroupClientPlaces, \
    Employee, \
    Client

from db_access import \
    AdminAccess, \
    EmployeeAccess, \
    CorporationAccess, \
    CompanyAccess, \
    GroupClientPlacesAccess, \
    ClientPlaceAccess, UserAccess


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = UserAccess(username=username.data.strip()). \
            users_by_username()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        users = UserAccess(email=email.data.strip()).users_by_email()
        if users is not None:
            raise ValidationError('Please use a different Email.')


# Form creator Corporation
class CorporationForm(FlaskForm):
    name_corporation = StringField('Enter name new corporation',
                                   validators=[DataRequired()])
    submit_corporation = SubmitField('Submit')
    cancel_corporation = SubmitField('Cancel')

    def validate_name_corporation(self, name_corporation):
        corporation = CorporationAccess(name=name_corporation.data.strip()). \
            same_corporation_name_for_creator_user()
        if corporation is not None:
            raise ValidationError('Please use a different Corporation name.')


# Form creator Admin
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


# Form creator Company
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
            raise ValidationError('Please use a different company name.')


# Form creator Employee
class EmployeeForm(FlaskForm):
    first_name_employee = StringField('First name', validators=[DataRequired()])
    email_employee = StringField('Email', validators=[DataRequired(), Email()])
    role_employee = SelectField('Role', validate_choice=False)

    submit_employee = SubmitField('Submit')
    cancel_employee = SubmitField('Cancel')

    def __init__(self, roles_to_choose, corporation_id, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.email_employee.choices = roles_to_choose
        self.role_employee.choices = roles_to_choose
        self.corporation_id = corporation_id

    def validate_email_employee(self, email_employee):
        employees = EmployeeAccess(corporation_id=self.corporation_id,
                                   email=self.email_employee.data.strip()). \
            employees_in_corporation_by_email()

        if employees is not None:
            raise ValidationError('Please use a different Email.')


# Form creator Group
class GroupClientPlacesForm(FlaskForm):
    name_group_client_places = StringField('Enter name new group',
                                           validators=[DataRequired()])
    submit_group_client_places = SubmitField('Submit')
    cancel_group_client_places = SubmitField('Cancel')

    def __init__(self, company_id, *args, **kwargs):
        super(GroupClientPlacesForm, self).__init__(*args, **kwargs)
        self.company_id = company_id

    def validate_name_group_client_places(self, name_group_client_places):
        group_client_places = GroupClientPlacesAccess(
            name=name_group_client_places.data.strip(),
            company_id=self.company_id).group_client_places_in_company_by_name()
        if group_client_places is not None:
            raise ValidationError('Please use a different group name.')


# Form creator Client Place
class ClientPlaceForm(FlaskForm):
    name_client_place = StringField('Enter name client place',
                                    validators=[DataRequired()])
    group_client_places = SelectField('Group', validate_choice=False)
    submit_client_place = SubmitField('Submit')
    cancel_client_place = SubmitField('Cancel')

    def __init__(self, company_id,
                 choices_group_client_places, *args, **kwargs):
        super(ClientPlaceForm, self).__init__(*args, **kwargs)
        self.company_id = company_id
        self.group_client_places.choices = choices_group_client_places

    def validate_name_client_place(self, name_client_place):
        client_place = ClientPlaceAccess(company_id=self.company_id,
                                         name=name_client_place.data.strip()). \
            client_place_in_company_by_name()

        if client_place is not None:
            raise ValidationError('Please use a different place name.')


# Profile editor
class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    about = TextAreaField('About user', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('cancel')

    def __init__(self, user, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, username):
        if username.data.lower() != self.user.username.lower():
            user = UserAccess(username=self.username.data.strip()).\
                users_by_username()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data.lower() != self.user.email.lower():
            users = UserAccess(email=self.email.data.strip()).users_by_email()

            if users is not None:
                raise ValidationError('Please use a different Email.')


# Company editor
class EditCompanyForm(FlaskForm):
    name = StringField('Name company', validators=[DataRequired()])
    about = TextAreaField('About company', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, original_name_company, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)
        self.original_name_company = original_name_company

    def validate_name(self, name):
        if name.data != self.original_name_company:
            company = Company.query. \
                filter_by(creator_user_id=current_user.id,
                          name=name.data.strip()).first()
            if company is not None:
                raise ValidationError('Please use a different company name.')


# Form Group editor
class EditGroupClientPlacesForm(FlaskForm):
    name = StringField('Enter name new group',
                       validators=[DataRequired()])
    about = TextAreaField('About group',
                          validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, company_id, original_name_group_client_places,
                 original_about, *args, **kwargs):
        super(EditGroupClientPlacesForm, self).__init__(*args, **kwargs)
        self.company_id = company_id
        self.original_name_group_client_places = \
            original_name_group_client_places
        self.original_about = original_about

    def validate_name(self, name):
        if name.data != self.original_name_group_client_places:
            group_client_places = GroupClientPlaces.query. \
                filter_by(company_id=self.company_id,
                          name=name.data.strip()).first()
            if group_client_places is not None:
                raise ValidationError('Please use a different group name.')


# Client Place editor
class EditClientPlaceForm(FlaskForm):
    name = StringField('Enter name client place',
                       validators=[DataRequired()])
    group_client_places = SelectField('Group', validate_choice=False)
    submit = SubmitField('Submit')

    def __init__(self, company_id, original_name_place,
                 choices_group_client_places, *args, **kwargs):
        super(EditClientPlaceForm, self).__init__(*args, **kwargs)
        self.company_id = company_id
        self.original_name_place = original_name_place
        self.group_client_places.choices = choices_group_client_places

    def validate_name(self, name):
        if name.data != self.original_name_place:
            client_place = ClientPlace.query. \
                filter_by(company_id=self.company_id,
                          name=name.data.strip()).first()
            if client_place is not None:
                raise ValidationError('Please use a different place name.')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ChoiceClientPlaceForm(FlaskForm):
    choices = MultiCheckboxField(coerce=int)
    submit_choice_client_places = SubmitField("Submit")


# This form for creating and editing Person
class PersonForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    about = TextAreaField('About user', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, original_first_name, original_last_name, original_about,
                 *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.original_first_name = original_first_name
        self.original_last_name = original_last_name
        self.original_about = original_about
