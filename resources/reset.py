"""
For resetting the password
"""

from flask import  render_template
from flask_jwt_extended import decode_token
from services.mail_services import email
from database.models import *

class Forgot(Resource):
    @api.expect(forgot_details)
    def post(self):
        """
        Forgot password
        :return: sent when mail is sent to desired email which is requested for resetting password
        """
        try:
            url = request.host_url + 'auth/reset/'
            body = request.get_json()
            if body == None:
                raise SchemaValidationError
            user_email = body.get('email')
            if not user_email:
                raise EmailDoesnotExistsError
            user = User.query.filter_by(email=user_email).first()
            if user is None:
                raise EmailDoesnotExistsError
            name = user.name.split()
            expires = dt.timedelta(hours=24)
            reset_token = create_access_token(identity=str(user.id), expires_delta=expires)
            email(recipients=[body.get('email')],
                         text_body= render_template('email/reset_password.txt',user=name[0],url=url + reset_token),
                         html_body=render_template('email/reset_password.html',user=name[0], url=url + reset_token)
                         )
            return {'message':'success', 'token':reset_token}, 200
            #return 'sent'
        except SchemaValidationError:
            raise BadRequest('Fields not filled')
        except EmailDoesnotExistsError:
            raise BadRequest('User with email {} not exists'.format(str(user_email)))

class Reset(Resource):
    @api.expect(reset_details)
    def post(self,token):
        """
        Reset password
        :param token: new token for resetting password
        :return: success when password is reset'ed
        """
        url = request.host_url + 'auth/reset/<token>'
        try:
            body = request.get_json()
            #reset_token = body.get('reset_token')
            password = body.get('password')
            re_password = body.get('confirm_password')
            #token = body.get('token')

            if not password:
                raise SchemaValidationError
            if token == None:
                raise BadRequest('Fields not filled')
            if password != re_password:
                raise BadRequest('Password not matched!!')

            user_id = decode_token(token)['identity']

            user = User.query.filter_by(id=user_id).first()

            user.password = password
            user.hash_password()
            db.session.commit()
            name = user.name.split()

            email(recipients=[user.email],
                  html_body= render_template('email/reset_successful.html',user=name[0]),
                  text_body=render_template('email/reset_successful.txt',user=name[0]))
            return {'message': 'success','token':token}, 200
        except SchemaValidationError:
            raise BadRequest('Fields not filled')
        except ExpiredSignatureError:
            raise BadRequest('Token is expired')
        except (DecodeError, InvalidTokenError):
            raise BadTokenError
        except BadTokenError:
            raise BadRequest('Invalid Token, try again')

