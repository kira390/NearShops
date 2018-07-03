"""
This file contains:
    - All Global variables and their default values
    - Functions,Objects used by multiple resources
"""
import os
import time
import re

import jwt
from flask_restful import abort


def isValidEmail(email):
    """
    Check if an email is valid
    :param email:
    :return True or False:
    """
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email) is not None:
        return True
    return False

def validate_token(access_token, public_key, auth_host, auth_algo):
    """
    This method check if a Token is valid and return the authenticated user
    :param access_token to validate:
    :param public_key to verify the access_token:
    :param auth_server who delivered the access_token:
    :param algorithm used to sign the access_token:
    :return the authenticated user or False if the token is not valid:
    """
    with open(public_key, 'r') as file:
        public_key = file.read()
    try:
        decoded_token = jwt.decode(access_token.encode(), public_key, issuer=auth_host, algorithm=auth_algo, algorithms=[auth_algo])

    except (jwt.exceptions.InvalidTokenError,
            jwt.exceptions.InvalidSignatureError,
            jwt.exceptions.InvalidIssuerError,
            jwt.exceptions.ExpiredSignatureError) as e:
        return False
    return decoded_token


def generate_access_token(user, pivate_key, auth_host, token_ttl, auth_algo):
    """
    This function generates a new JWT token to authenticate user in other services
    :param user to generate the token for:
    :param pivate_key:
    :param auth_host:
    :param token_ttl:
    :param auth_algo:
    :return the generated access token:
    """
    with open(pivate_key, 'rb') as f:
        private_key = f.read()
    if private_key is None:
        abort(400, "Invalid Server private key")
    payload = {
        "iss": auth_host,
        "exp": time.time() + token_ttl,
        "user": user
    }
    access_token = jwt.encode(payload, private_key, algorithm=auth_algo)
    return {
        "access_token": access_token.decode(),
        "token_type": "JWT",
        "expire_in": token_ttl
    }

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
    app.config['MONGO_DBNAME'] = 'authservice'
    app.config['MONGO_URI'] = 'mongodb://shopproxy:azerty@localhost:27017/'
    app.config['PUBLIC_KEY'] = 'public.pem'
    app.config['PRIVATE_KEY'] = 'private.pem'
    app.config['AUTH_ALGO'] = 'RS256'
    app.config['AUTH_HOST'] = 'localhost'
    app.config['TOKEN_TTL'] = 20

    for key in app.config.keys():
        if key in os.environ:
            app.config[key]=os.environ[key]

    app.config['TOKEN_TTL'] = float(app.config['TOKEN_TTL'])