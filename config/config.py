import os
from config.settings import Settings

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or Settings.secret_key

    SQLALCHEMY_DATABASE_URI = Settings.sqlalchemy_database_uri

    # SQLALCHEMY_DATABASE_URI = os.environ.get('QR_DATABASE_URL') or \
    #                           'sqlite:///' + os.path.join(basedir, 'QR_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Email server
    MAIL_SERVER = Settings.mail_server
    MAIL_PORT = Settings.mail_port
    MAIL_USE_TLS = Settings.mail_use_tls
    MAIL_USERNAME = Settings.mail_username
    MAIL_PASSWORD = Settings.mail_password
    ADMINS = Settings.admins


