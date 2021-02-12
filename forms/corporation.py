from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     TextAreaField)

from wtforms.validators import (DataRequired,
                                ValidationError,
                                Length)

from db_access import CorporationAccess


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


class EditCorporationForm(FlaskForm):
    name = StringField('Name corporation', validators=[DataRequired()])
    about = TextAreaField('About corporation',
                          validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, original_name_corporation, *args, **kwargs):
        super(EditCorporationForm, self).__init__(*args, **kwargs)
        self.original_name_corporation = original_name_corporation

    def validate_name(self, name):
        if name.data.strip().lower() != self.original_name_corporation.lower():
            corporation = CorporationAccess(name=name.data.strip()). \
                same_corporation_name_for_creator_user()
            if corporation is not None:
                raise ValidationError(
                    'Please use a different Corporation name.')
