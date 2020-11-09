from models import Admin
from app import db


def create_creator_admin(creator_user_id, about, email, phone, user_id,
                         corporation_id):
    admin = Admin(creator_user_id=creator_user_id, active=True, about=about,
                  email=email, phone=phone, role_admin_id=1, user_id=user_id,
                  corporation_id=corporation_id)
    db.session.add(admin)
    return admin


def create_admin(creator_user_id, about, email, phone, role_admin_id,
                 corporation_id):
    admin = Admin(creator_user_id=creator_user_id, about=about, email=email,
                  phone=phone, role_admin_id=role_admin_id,
                  corporation_id=corporation_id)
    db.session.add(admin)
    db.session.commit()
    return admin