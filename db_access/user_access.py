from models import User
from app import db


def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def user_by_slug(user_slug):
    user = User.query.filter_by(slug=user_slug).first()
    return user


def user_by_slug_or_404(user_slug):
    user = User.query.filter_by(slug=user_slug).first_or_404()
    return user


def user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user


def user_by_id_or_404(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return user
