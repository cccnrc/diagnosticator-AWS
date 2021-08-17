import os
from dotenv import load_dotenv

### this is to specify that I can also put these variables in a file called .env in main folder
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    ### DATABASE_URL
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'DB', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = ['cocchi.e89@gmail.com']
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = bool( int( os.environ.get('MAIL_USE_TLS') ) )
    MAIL_USE_SSL = bool( int( os.environ.get('MAIL_USE_SSL') ) )
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    VARIANT_DB = os.environ.get('VARIANT_DB')
    TOKEN_EXP_SEC = os.environ.get('TOKEN_EXP_SEC')
    TOKEN_RESTORE_EXP_SEC = os.environ.get('TOKEN_RESTORE_EXP_SEC')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')
    SES_REGION_NAME = os.environ.get('SES_REGION_NAME')
    SES_EMAIL_SOURCE = os.environ.get('SES_EMAIL_SOURCE')
    CREDENTIALS_URL = os.environ.get('CREDENTIALS_URL')
    SERVER_NAME = os.environ.get('SERVER_NAME')
