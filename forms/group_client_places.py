from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     TextAreaField)

from wtforms.validators import (DataRequired,
                                ValidationError,
                                Length)

from models import GroupClientPlaces

from db_access import GroupClientPlacesAccess


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
        if name.data.strip().lower() \
                != self.original_name_group_client_places.lower():
            group_client_places = GroupClientPlaces.query. \
                filter_by(company_id=self.company_id,
                          name=name.data.strip()).first()
            if group_client_places is not None:
                raise ValidationError('Please use a different group name.')
