from models import Admin
from app import db


def create_add_admin(about, email, phone, role, user_id, corporation_id):
    admin = Admin(about=about, email=email, phone=phone, role=role,
                  user_id=user_id, corporation_id=corporation_id)
    db.session.add(admin)
    return admin.id


def create_admin(about, email, phone, role, user_id, corporation_id):
    admin_id = create_add_admin(about, email, phone, role, user_id,
                                corporation_id)
    db.session.commit()
    return admin_id

