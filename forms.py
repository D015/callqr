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

from datetime import datetime


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
        user = User.query.filter_by(username=username.data.strip()).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Profile editor
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about = TextAreaField('About user', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('cancel')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data.strip()). \
                first()
            if user is not None:
                raise ValidationError('Please use a different username.')


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


# This form for creating and editing Employee
class EmployeeForm(FlaskForm):
    about = TextAreaField('About user', validators=[Length(min=0, max=140)])
    email = StringField('Email', validators=[DataRequired()])
    phone_number_telegram = StringField('Phone number telegram',
                                        validators=[DataRequired()])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, original_about, original_email,
                 original_phone_number_telegram, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.original_about = original_about
        self.original_email = original_email
        self.original_phone_number_telegram = original_phone_number_telegram

    def validate_email(self, email):
        if email.data != self.original_email:
            employee = Employee.query.filter \
                (Employee.email == email.data.strip()).first()

            user = User.query.filter\
                (User.email == email.data.strip(),
                 User.person != current_user.person).first()

            client = Client.query.filter\
                (User.email == email.data.strip(),
                 User.person != current_user.person).first()

            if user is not None or employee is not None or client is not None:
                raise ValidationError('Please use a different email address.')


# Form creator Company
class CompanyForm(FlaskForm):
    name = StringField('Enter name new company',
                       validators=[DataRequired()])
    about = TextAreaField('About company', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def validate_name(self, name):
        company = Company.query. \
            filter_by(creator_user_id=current_user.id,
                      name=name.data.strip()).first()
        if company is not None:
            raise ValidationError('Please use a different company name.')


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


# Form creator Group
class GroupClientPlacesForm(FlaskForm):
    name_group_client_places = StringField('Enter name new group',
                                           validators=[DataRequired()])
    about = TextAreaField('About group', validators=[Length(min=0, max=140)])
    submit_group_client_places = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, company_id, *args, **kwargs):
        super(GroupClientPlacesForm, self).__init__(*args, **kwargs)
        self.company_id = company_id

    def validate_name_group_client_places(self, name_group_client_places):
        group_client_places = GroupClientPlaces.query. \
            filter_by(company_id=self.company_id,
                      name=name_group_client_places.data.strip()).first()
        if group_client_places is not None:
            raise ValidationError('Please use a different group name.')


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


# Form creator Client Place
class ClientPlaceForm(FlaskForm):
    name_client_place = StringField('Enter name client place',
                                    validators=[DataRequired()])
    group_client_places = SelectField('Group', validate_choice=False)
    submit_client_place = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, company_id,
                 choices_group_client_places, *args, **kwargs):
        super(ClientPlaceForm, self).__init__(*args, **kwargs)
        self.company_id = company_id
        self.group_client_places.choices = choices_group_client_places

    def validate_name_client_place(self, name_client_place):
        client_place = ClientPlace.query. \
            filter_by(company_id=self.company_id,
                      name=name_client_place.data.strip()).first()
        if client_place is not None:
            raise ValidationError('Please use a different place name.')


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
