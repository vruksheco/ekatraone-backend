class InternalServerError(Exception):
    pass

class SchemaValidationError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class UpdatingUserError(Exception):
    pass

class DeletingUserError(Exception):
    pass

class UserNotExistsError(Exception):
    pass

class EmailAlreadyExistsError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

class EmailDoesnotExistsError(Exception):
    pass

class BadTokenError(Exception):
    pass

class ExpiredTokenError(Exception):
    pass

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
     "SchemaValidationError": {
         "message": "Request is missing the required fields",
         "status": 400
     },
     "UserAlreadyExistsError": {
         "message": "User with given name already exists",
         "status": 400
     },
     "UpdatingUserError": {
         "message": "Updating user added by other is forbidden",
         "status": 403
     },
     "DeletingUserError": {
         "message": "Deleting user added by other is forbidden",
         "status": 403
     },
     "UserNotExistsError": {
         "message": "User with given id doesn't exists",
         "status": 400
     },
     "EmailAlreadyExistsError": {
         "message": "User with given email address already exists",
         "status": 400
     },
     "UnauthorizedError": {
         "message": "Invalid username or password",
         "status": 401
     },
     "EmailDoesnotExistsError": {
         "message": "Couldn't find the user with given email address",
         "status": 400
     },
     "BadTokenError": {
        "message": "Invalid token",
        "status": 403
      },
    "ExpiredTokenError": {
        "message":"Token is expired",
        "status": 403
    }
 }
