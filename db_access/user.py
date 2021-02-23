from flask_login import current_user
from sqlalchemy import or_

from db_access.base import BaseAccess
from models import User
from utils.utils_add import add_commit


class UserAccess(BaseAccess):
    def __init__(self, id=None, slug=None, _obj=None, username=None, email=None,
                 about=None, password=None):
        super().__init__(id, slug, _obj, model=User)

        self.username = username
        self.email = email
        self.password = password
        self.about = about

    def create_user(self):
        user = User(username=self.username, email=self.email)
        user.set_password(self.password)
        add_commit(user)
        return user

    def the_current_user(self):
        return current_user

    def the_current_user_of_model(self):
        user = User.query.filter_by(id=current_user.id).first_or_404()
        return user

    def users_by_email(self):
        users = User.query.filter(User.email.ilike(self.email)).first()
        return users

    def users_by_username(self):
        users = User.query.filter(User.username.ilike(self.username)).first()
        return users

    def user_by_username_or_email(self):
        user = User.query.filter(or_(User.username == self.username,
                                     User.email == self.email)).first()
        return user