from flask_wtf import FlaskForm
from wtforms import (SubmitField,
                     BooleanField,
                     SelectMultipleField,
                     widgets)
from wtforms.validators import ValidationError

from db_access import BaseAccess


class ActiveArchivedForm(object):
    active = BooleanField('Active')
    archived = BooleanField('Archived')


class RemoveObjectForm(FlaskForm):
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

    def __init__(self, obj, *args, **kwargs):
        super(RemoveObjectForm, self).__init__(*args, **kwargs)
        self.obj = obj

    def validate_submit(self, submit):
        role = getattr(self.obj, 'role_id', None)
        if role == 100:
            raise ValidationError('Administrator creator cannot be deleted')

        is_obj = BaseAccess(_obj=self.obj).object_is_exist()
        if is_obj is not True:
            raise ValidationError('This object no longer exists')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ChoiceClientPlaceForm(FlaskForm):
    choices = MultiCheckboxField(coerce=int)
    submit_choice_client_places = SubmitField("Submit")
