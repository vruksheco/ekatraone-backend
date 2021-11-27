"""
About the users
"""

from database.schemas_database import *

class Details(Resource):
    @jwt_required
    def get(self):
        """
        Retrieving all the users
        :return: details of the users
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                raise UnauthorizedError
            details = User.query.order_by(User.id).all()
            if not details:
                return UserNotExistsError
            output = user_schemas.dump(details)
            return {'users':output}, 200
        except UserNotExistsError:
            raise BadRequest('User with this details not exists')
        except (WrongTokenError, InvalidTokenError):
            raise BadRequest('Token is invalid')
        except InvalidHeaderError:
            raise BadRequest("Bad Authorization error\
            Expected 'Bearer <jwt>'")
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except UnauthorizedError as e:
            print(e)
            raise BadRequest('Token is missing')
        except (NoAuthorizationError,UnauthorizedError):
            raise BadRequest('Missing Authorization Header')
        except Exception as e:
            print(e)
            raise e


class UpdateDetails(Resource):
    @jwt_required
    def get(self,id):
        """
        Retrieving one user
        :param id: user id
        :return: details of the user
        """
        try:
            #user_id = get_jwt_identity()
            detail = User.query.filter_by(id=id).first()
            if not detail:
                raise UserNotExistsError
            output = user_schema.dump(detail)
            return output
        except UserNotExistsError:
            raise BadRequest('User with {} not exists'.format(str(id)))
        except NoAuthorizationError:
            raise UnauthorizedError
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')

    @jwt_required
    def delete(self,id):
        """
        deleting the user
        :param id: user id
        :return: success if user is deleted
                    else raises 404 error if user is not found
        """
        try:
            user_id = get_jwt_identity()
            if user_id is None:
                raise UnauthorizedError
            user = User.query.filter_by(id=id).first()
            if not user:
                raise UserNotExistsError
            delete_user(id)
            return {"message":"Deleted successfully"}, 200
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(id))
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')


    @jwt_required
    @ns_user.expect(user)
    def put(self,id):
        """
        Updates the user
        :param id: user id
        :return: success if user is updated
        """
        try:
            user_id = get_jwt_identity()
            if user_id == None:
                raise UnauthorizedError
            details = User.query.filter_by(id=id).first()
            if not details:
                raise UserNotExistsError
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            details.name = body.get('name')
            details.email = body.get('email')
            details.contact = body.get('contact')
            details.organization = body.get('organization')
            details.role = body.get('role')
            details.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            User(**body, updated_date=details.updated_date)
            db.session.commit()
            return {'message':'Update Successful'},200
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(id))
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
