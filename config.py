import os
import settings


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or settings.secret_key

    SQLALCHEMY_DATABASE_URI = settings.sqlalchemy_database_uri

    # SQLALCHEMY_DATABASE_URI = os.environ.get('QR_DATABASE_URL') or \
    #                           'sqlite:///' + os.path.join(basedir, 'QR_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Email server
    MAIL_SERVER = settings.mail_server
    MAIL_PORT = settings.mail_port
    MAIL_USE_TLS = settings.mail_use_tls
    MAIL_USERNAME = settings.mail_username
    MAIL_PASSWORD = settings.mail_password
    ADMINS = settings.admins


