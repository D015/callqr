from flask_login import current_user

from models import User
from app import db


class UserAccess:
    def __init__(self, id=None, slug=None, username=None, email=None,
                 password=None):
        
        self.id = id
        self.slug = slug
        self.username = username
        self.email = email
        self.password = password
        

    def create_user(self):
        user = User(username=self.username, email=self.email)
        user.set_password(self.password)
        db.session.add(user)
        db.session.commit()
        return user
    
    
    def user_by_slug(self):
        user = User.query.filter_by(slug=self.slug).first()
        return user
    
    
    def user_by_slug_or_404(self):
        user = User.query.filter_by(slug=self.slug).first_or_404()
        return user
    
    
    def user_by_id(self):
        user = User.query.filter_by(id=self.id).first()
        return user
    
    
    def user_by_id_or_404(self):
        user = User.query.filter_by(id=self.id).first_or_404()
        return user
    
    
    def the_current_user(self):
        return current_user
    
    
    def admins_of_current_user(self):
        return current_user.admins.filter_by(active=True, archived=False)
    
    
    def employees_of_current_user(self):
        return current_user.employees.filter_by(active=True, archived=False)
    
    
    def clients_of_current_user(self):
        return current_user.clients.filter_by(active=True, archived=False)
