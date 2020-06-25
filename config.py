import os

ENV = os.environ.get('FLASK_ENV')

if ENV == 'development':
    DEBUG = True
else:
    DEBUG = False

ROOT_URL = os.environ.get('FLASK_ROOT_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
FACEBOOK_OAUTH_CLIENT_ID = os.environ.get('FACEBOOK_OAUTH_CLIENT_ID')
FACEBOOK_OAUTH_CLIENT_SECRET = os.environ.get('FACEBOOK_OAUTH_CLIENT_SECRET')
FB_GRAPH_API = 'https://graph.facebook.com/v3.0/'
FB_MSG_API_URL = 'https://graph.facebook.com/v3.0/me/messages'
FB_VERIFY_TOKEN = os.environ.get('FACEBOOK_VERIFY_TOKEN')
FB_PAGE_ACCESS_TOKEN = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
OAUTHLIB_RELAX_TOKEN_SCOPE = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
