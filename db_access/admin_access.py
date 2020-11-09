from models import Admin
from app import db


def create_add_admin(about, email, phone, role_admin_id, user_id,
                     corporation_id):
    admin = Admin(about=about, email=email, phone=phone,
                  role_admin_id=role_admin_id, user_id=user_id,
                  corporation_id=corporation_id)
    db.session.add(admin)
    return admin


def create_admin(about, email, phone, role_admin_id, user_id, corporation_id):
    admin = create_add_admin(about, email, phone, role_admin_id, user_id,
                             corporation_id)
    db.session.commit()
    return admin
