from flask_wtf import FlaskForm

from wtforms import (SubmitField,
                     StringField,
                     PasswordField,
                     BooleanField,
                     TextAreaField)
from wtforms.validators import (DataRequired,
                                ValidationError,
                                EqualTo,
                                Email,
                                Length)

from db_access import UserAccess


class LoginForm(FlaskForm):
    username_or_email = StringField('Username or email', validators=[DataRequired()])
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
        if username.data.lower() != self.user.username_or_email.lower():
            user = UserAccess(username=self.username.data.strip()). \
                users_by_username()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data.strip().lower() != self.user.email.lower():
            users = UserAccess(email=self.email.data.strip()).users_by_email()

            if users is not None:
                raise ValidationError('Please use a different Email.')
