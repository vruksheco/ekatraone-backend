"""
This is the main app which connects all the .py files and configuring the flask and others
"""

from modules_and_libraries import *


# initializing app with flask
app = Flask(__name__)

#initializing CORS
CORS(app=app)
cors = CORS(app, resources={
    r"/*":{
        "origins":"*"
    }
})

#Database server
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SWAGGER_UI_JSONEDITOR'] = config.SWAGGER_UI_JSONEDITOR
#JWT
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_HEADER_NAME'] = config.JWT_HEADER_NAME
app.config['JWT_HEADER_TYPE'] = config.JWT_HEADER_TYPE
#CORS Header
app.config['CORS_HEADERS'] = config.CORS_HEADER

#Mail Server
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
mail = Mail(app=app)

authorizations = {
    'Authorization': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

#initializing API
api = Api(app, version='2.0', title='ekatra-backend', description='UserDetails',authorizations=authorizations,
          security='Authorization', errors=errors)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy',url=config.SQLALCHEMY_DATABASE_URI, alias='db')
scheduler.start()

#initializing namespace
ns_auth = api.namespace('auth', description='auth related, login, signup, reset, forgot')
ns_user = api.namespace('user', description='user account related, user_listing etc..')
ns_course = api.namespace('course', description='course related')
ns_user_group = api.namespace('group', description='groups related')
ns_delivery = api.namespace('delivery', description='schedule delivery related')
ns_dashboard = api.namespace('dashboard', description='Dashboard pages')
ns_whatsapp = api.namespace('whatsapp', description='Api for viewing the message history')

files = RequestParser(bundle_errors=True)
files.add_argument('uploadfile',location='files',type=FileStorage,required=False)
files.add_argument('course_id',type=int)
files.add_argument('day',type=int)
#Models
login = api.model('LOGIN', {
    'email': fields.String(required=True, unique=True, example='example@gmail.com'),
    'password': fields.String(required=True, example=' ')
})
signup = api.model('SIGNUP', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True, example='name'),
    'email': fields.String(required=True, example='email@gmail.com'),
    'contact': fields.Integer(required=True, example=9999999999),
    'password': fields.String(required=True, example='password')
})

user = api.model('USERDETAILS', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True, example='name'),
    'email': fields.String(required=True, example='email@gmail.com'),
    'contact': fields.Integer(required=True, example=9999999999),
    'organization': fields.String(required=False, example='organization'),
    'role': fields.String(required=False, example='student/faculty')
})

forgot_details = api.model('FORGOT', {
    'email': fields.String(required=True, example='email@gmail.com')
})

reset_details = api.model('RESET', {
    'password': fields.String(required=True, example='enter the new password'),
    'confirm_password':fields.String(required=True, example='re-enter your password')
})

questions = api.model('QUESTIONS',{
    'question': fields.String(required=True,attribute='text'),
    'type': fields.String(required=True,attribute='question-type'),
    'correct_answer': fields.String(required=True)

})

days_of_courses = api.model('DAYS',{
    'day':fields.Integer(readonly=True),
    'text':fields.String(description='text1',attribute='day_text',required=True),
    'questions':fields.List(fields.Nested(questions,skip_none=True))
})

detail_courses = api.model('COURSES',{
    'id':fields.Integer(readonly=True),
    'name':fields.String(required=True, example='coursename'),
    'author':fields.String(required=True, example='author'),
    'description':fields.String(required=True),
    'days':fields.List(fields.Nested(days_of_courses, skip_none=True))
})

students = api.model('STUDENTS',{
    'name': fields.String(required=True,example='name'),
    'number': fields.String(required=True,example="999999999",attribute='phone-number'),
    'channel': fields.String(required=True,attribute='channel_name',example='channelname'),
    'is_subscribed': fields.Boolean(required=True, example=True),
    'country_code': fields.String(required=True, example='+91')
})

detail_groups = api.model('GROUPS',{
    'id':fields.Integer(readonly=True),
    'name':fields.String(required=True),
    'description':fields.String(required=True),
    'students': fields.List(fields.Nested(students,skip_none=True))
})

delivery_field = api.model('DELIVERY',{
    'schedule_at': fields.DateTime(required=True, example="YYYY-MM-DD HH:MM")
})

# error handlers

@api.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    return {'message': str(e)}, 401


@api.errorhandler(CSRFError)
def handle_csrf_error(e):
    return {'message': str(e)}, 401


@api.errorhandler(ExpiredSignatureError)
def handle_expired_error(e):
    return {'message': 'Token has expired'}, 401


@api.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(InvalidTokenError)
def handle_invalid_token_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(JWTDecodeError)
def handle_jwt_decode_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(WrongTokenError)
def handle_wrong_token_error(e):
    return {'message': str(e)}, 422


@api.errorhandler(RevokedTokenError)
def handle_revoked_token_error(e):
    return {'message': 'Token has been revoked'}, 401


@api.errorhandler(FreshTokenRequired)
def handle_fresh_token_required(e):
    return {'message': 'Fresh token required'}, 401


@api.errorhandler(UserLoadError)
def handler_user_load_error(e):
    # The identity is already saved before this exception was raised,
    # otherwise a different exception would be raised, which is why we
    # can safely call get_jwt_identity() here
    identity = get_jwt_identity()
    return {'message': "Error loading the user {}".format(identity)}, 401


@api.errorhandler(UserClaimsVerificationError)
def handle_failed_user_claims_verification(e):
    return {'message': 'User claims verification failed'}, 401

@api.errorhandler(TypeError)
def handle_type_error(e):
    return {'message': str(e)}, 400

@app.errorhandler(500)
def handle_500_error(e):
    return {'message': str(e)}

@api.errorhandler(NameError)
def handle_name_error(e):
    return {'message': str(e)}, 400

@api.errorhandler(SyntaxError)
def handle_syntax_error(e):
    return {'message': str(e)}, 400

@api.errorhandler(AttributeError)
def handle_attribute_error(e):
    return {'message': str(e)}, 400

@api.errorhandler(IndentationError)
def handle_indentation_error(e):
    return {'message': str(e)}, 405

@api.errorhandler(KeyError)
def handle_key_error(e):
    return {'KeyError': 'missing'+str(e)+'key'}, 400

