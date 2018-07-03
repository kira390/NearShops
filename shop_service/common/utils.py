"""
This file contains:
    - All Global variables and their default values
    - Functions,Objects used by multiple resources
"""
import os

import jwt
from flask_restful import abort


def validate_token(access_token, public_key, auth_server, algorithm):
    """
    This function check if a Token is valid and return the authenticated user
    :param access_token to validate:
    :param public_key to verify the access_token:
    :param auth_server who delivered the access_token:
    :param algorithm used to sign the access_token:
    :return the authenticated user or False if the token is not valid:
    """
    with open(public_key,'r') as file:
        public_key=file.read()
    try:
        decoded_token = jwt.decode(access_token.encode(), public_key, issuer=auth_server,algorithm=algorithm)
    except (jwt.exceptions.InvalidTokenError,
            jwt.exceptions.InvalidSignatureError,
            jwt.exceptions.InvalidIssuerError,
            jwt.exceptions.ExpiredSignatureError):
        return False
    return decoded_token


def is_authenticated(request, public_key, auth_host, auth_algo, role="regular"):
    """
    This function check the validity of Token:
    :param access_token:
    :param the expected role of the user:
    :return the user object or False if there is no token or the role is not matched:
    """
    authorization = request.headers.get('Authorization')
    if authorization is None or 'Bearer' not in authorization:
        abort(401, message='You are not authenticated')

    auth_token = validate_token(authorization[7:], public_key, auth_host, auth_algo)
    if authorization[7:] and auth_token:
        if auth_token["user"]["role"] in [role, 'admin']:
            return auth_token["user"]
        else:
            abort(401, message="you don't have the right privileges")
    else:
        abort(400, message='Invalid Access Token')


def configure_envirement(app):
    app.config['APP_BIND'] = "0.0.0.0"
    app.config['APP_PORT'] = 80
    app.config['MONGO_DBNAME'] = 'shopservice'
    app.config['MONGO_URI'] = 'mongodb://shopproxy:azerty@localhost:27017/'
    app.config['PUBLIC_KEY'] = 'public.pem'
    app.config['AUTH_ALGO'] = 'RS256'
    app.config['AUTH_HOST'] = 'localhost'
    app.config['TOKEN_TTL'] = 20

    for key in app.config.keys():
        if key in os.environ:
            app.config[key]=os.environ[key]

    app.config['TOKEN_TTL'] = float(app.config['TOKEN_TTL'])