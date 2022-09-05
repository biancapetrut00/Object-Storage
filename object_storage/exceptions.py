from flask import jsonify

class BaseException(Exception):
    status_code = 500
    message = "Unexpected error"

    def __init__(self, message=None, status_code=None, payload=None):
        if message:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class Unauthorized(BaseException):
    status_code = 401
    message = "Unauthorized"

class Forbidden(BaseException):
    status_code = 403
    message = "Forbidden"

class NotFound(BaseException):
    status_code = 404
    message = "NotFound"

class Exists(BaseException):
    status_code = 409
    message = "Already exists"

class Conflict(BaseException):
    status_code = 409
    message = "User is already logged in"

