"""
This file contains:
    - All Global variables and their default values
    - Functions,Objects used by multiple resources
"""
import jwt
from flask_restful import reqparse, abort
from geopy import distance
from pymongo import MongoClient


# Authentication related parameters
AUTH_HOST = 'localhost'
AUTH_PUB = 'public.pem'
AUTH_ALGO = 'RS256'
LIFE_SPAN = 20

# Service host and port
APP_BIND = 'localhost'
APP_PORT = 5001

# MongoDB parameters:
MONGODB_URI = 'mongodb://shopproxy:azerty@localhost:27017/'
MONGODB_DBNAME = 'shopservice'

MONGO = MongoClient(MONGODB_URI)[MONGODB_DBNAME]

# Parses arguments to check if there is any location to filter on.
LOCATION_PARSER = reqparse.RequestParser()
LOCATION_PARSER.add_argument('latitude', type=float)
LOCATION_PARSER.add_argument('longitude', type=float)

# Parses arguments to chack if there is a shop object available.
SHOP_PARSER = reqparse.RequestParser()
SHOP_PARSER.add_argument('_id', type=str)
SHOP_PARSER.add_argument('name', type=str)
SHOP_PARSER.add_argument('address', type=str)
SHOP_PARSER.add_argument('longitude', type=float)
SHOP_PARSER.add_argument('latitude', type=float)


def sort_shops_by_distance(shops, location):
    """
    This Function sorts a list of shop by distance from a location
    :param shops:
    :param location:
    :return Sorted Shop List:
    """
    result = []
    for shop in shops:
        shop_location = (shop["longitude"], shop["latitude"])
        shop["distance"] = distance.vincenty(location, shop_location).km
        result.append(shop)
        result = sorted(result, key=lambda k: k['distance'])
    return result


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


def is_authenticated(request,role="regular"):
    """
    This Function check the validity of Token:
    :param access_token:
    :param the expected role of the user:
    :return the user object or False if there is no token or the role is not matched:
    """
    authorization = request.headers.get('Authorization')
    if authorization is None or 'Bearer' not in authorization:
        abort(401, message='You are not authenticated')

    auth_token = validate_token(authorization[7:], AUTH_PUB, AUTH_HOST, AUTH_ALGO)
    if authorization[7:] and auth_token:
        if auth_token["user"]["role"] in [role, 'admin']:
            return auth_token["user"]
        else:
            abort(401, message="you don't have the right privileges")
    else:
        abort(400, message='Invalid Access Token')