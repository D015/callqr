from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     SelectField)

from wtforms.validators import (DataRequired,
                                ValidationError)

from db_access import ClientPlaceAccess


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
        if name.data.strip().lower() != self.original_name_place.lower():
            client_place = ClientPlaceAccess(
                company_id=self.company_id,
                name=name.data.strip()). \
                client_place_in_company_by_name()
            if client_place is not None:
                raise ValidationError('Please use a different place name.')
