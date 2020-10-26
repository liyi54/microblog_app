from flask_httpauth import HTTPTokenAuth
from app.models import User
from app.api.errors import error_response

token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_error_handler(status_code):
    return error_response(status_code)