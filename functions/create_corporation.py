from models import Corporation
from app import db
from functions import create_admin
from flask_login import current_user


def create_corporation(name, about):
    corporation = Corporation(name=name, about=about)
    try:
        db.session.add(corporation)
        db.session.flush()

        db.session.commit()
    except:
        db.session.rollback()
