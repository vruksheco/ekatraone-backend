"""
This is for sign up and login
"""

from database.models import *
class Signup(Resource):
    @ns_auth.expect(signup)
    def post(self):
        """
        Sign Up
        :return:success and stores new user in database
        """
        try:
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            user_name = body.get('name')
            user_email = body.get('email')
            user_contact = body.get('contact')
            user_password = body.get('password')
            if user_email is None or user_password is None:
                raise SchemaValidationError
            yes_user = User.query.filter_by(email=user_email).first()
            if yes_user:
                raise EmailAlreadyExistsError
            user = User(name=user_name, email=user_email, contact=user_contact, password=user_password, is_admin=False)
            #user = User(**body, is_admin=False)
            user.hash_password()
            db.session.add(user)
            user.created_date = dt.datetime.now().astimezone(pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            id = user.id
            return {'message':"Success", 'id':str(id)}, 200
        except SchemaValidationError:
            raise BadRequest('Fields not filled')
        except EmailAlreadyExistsError:
            db.session.rollback()
            raise BadRequest('User with email {} already exists'.format(user_email))



class Login(Resource):
    @ns_auth.expect(login)
    def post(self):
        """
        Login
        :return:jwt token for authorization
        """
        try:
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            email = body.get('email')
            password = body.get('password')
            if email is None or password is None:
                raise SchemaValidationError
            user = User.query.filter_by(email=body.get('email')).first()
            if not user:
                raise UserNotExistsError
            authorize = user.check_password(password=password)
            if not authorize:
                raise BadRequest('Either email or password is incorrect')
            id = user.id
            expires = dt.timedelta(days=config.EXPIRY_END_DAYS)
            access_token = create_access_token(identity=str(id), expires_delta=expires)
            user.token = access_token
            db.session.commit()
            return {'message': 'success', 'token':access_token}, 200
        except UserNotExistsError:
            raise BadRequest('User with email {} not exists'.format(email))
        except UnauthorizedError:
            raise BadRequest('Either email or password is incorrect')
        except SchemaValidationError:
            raise BadRequest('Required fields not filled')

