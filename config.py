"""
cofiguring the api
"""

import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
#SQLALCHEMY_DATABASE_URI = 'postgresql://tejas:nandamtejas1306@localhost/sample123'
#SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
EXPIRY_END_DAYS = 7
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
CORS_HEADER = os.environ['CORS_HEADER']
SQLALCHEMY_TRACK_MODIFICATIONS = True
JWT_HEADER_NAME = os.environ['JWT_HEADER_NAME']
JWT_HEADER_TYPE = os.environ['JWT_HEADER_TYPE']
SWAGGER_UI_JSONEDITOR = True
MAIL_SERVER = os.environ['MAIL_SERVER']
MAIL_DEFAULT_SENDER = os.environ['MAIL_DEFAULT_SENDER']
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
MAIL_PORT = os.environ['MAIL_PORT']
MAIL_USE_TLS = False
MAIL_USE_SSL = True
ACCOUNT_SID = os.environ['ACCOUNT_SID']
AUTH_TOKEN = os.environ['AUTH_TOKEN']
MESSAGING_SERVICE_SID = os.environ['MESSAGING_SERVICE_SID']
ACCESS_CONTROL_ALLOW_ORIGIN=os.environ['ACCESS_CONTROL_ALLOW_ORIGIN']
AWS_BUCKET = os.environ['AWS_BUCKET']
AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']
UPLOAD_FOLDER =os.path.join(os.path.abspath(os.path.dirname(__file__)),'statics','uploads')
MAX_CONTENT_LENGTH = 1024*1024*1024*1024
ALLOWED_EXTENSIONS = set(['txt','json', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mov','mp4','mp3','py','ipynb','pem','csv','wav','z','zip','pkg','bin','db','dab','xml','html','tar','email','eml','msg','vcf','apk','exe','com','fnt','fon','otf','ttf','bmp','ai','ico','ps','psd','svg','ppt','pptx','key','txt','xls','xlsx','mpg','mpeg','mkv','m4v','doc','docx','wpd','odt','rtf'])
