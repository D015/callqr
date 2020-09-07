from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

from config import Config
from flask_sqlalchemy import SQLAlchemy

# for migrate
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# from flask_bootstrap import Bootstrap

from flask_qrcode import QRcode


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

#for migrate
migrate = Migrate(app, db, render_as_batch=True)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

#Flask-Login initialization
login = LoginManager(app)
# User Login Requirement
login.login_view = 'login'

mail = Mail(app)

QRcode(app)

# bootstrap = Bootstrap(app)

import routes
import models
import errors