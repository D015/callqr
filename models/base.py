from datetime import datetime
from uuid import uuid4

from flask_login import current_user

from app import db


class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    creator_user_id = db.Column(db.Integer)
    # todo slug - primary_key=True
    slug = db.Column(db.String(128), index=True, unique=True)
    active = db.Column(db.Boolean(), default=True)
    archived = db.Column(db.Boolean(), default=False)

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)
        self.slug = uuid4().hex
        self.creator_user_id = current_user.id