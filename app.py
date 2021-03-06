from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

from config.config import Config
from flask_sqlalchemy import SQLAlchemy

# for migrate
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

import logging
from logging.handlers import RotatingFileHandler
import os

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

# logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/callqr.log', maxBytes=10240,
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.DEBUG)
app.logger.info('CallQR.com startup INFO')
app.logger.debug('CallQR.com startup DEBUG')

# bootstrap = Bootstrap(app)

import routes
import models
import utils.errors