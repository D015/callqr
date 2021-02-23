from app import db

employees_to_groups_client_places = db.Table(
    'employees_to_groups_client_places',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('group_client_places_id', db.Integer, db.ForeignKey(
        'group_client_places.id')))

employees_to_client_places = db.Table(
    'employees_to_client_places',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('client_place_id', db.Integer, db.ForeignKey('client_place.id')))