from models import Admin
from app import db


def create_admin(role, about, email, phone, user_id, corporation_id):
    admin = Admin(role=role, about=about, email=email, phone=phone,
                  user_id=user_id, corporation_id=corporation_id)
    db.session.add(admin)
    db.session.commit()
    return admin.id
