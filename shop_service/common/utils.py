"""
This file contains:
    - All Global variables and their default values
    - Functions,Objects used by multiple resources
"""
from flask_restful import reqparse
from geopy import distance
from pymongo import MongoClient

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


def is_authenticated(access_token,role="regular"):
    """
    TODO implement the authentication logic
    This Function check the validity of Token:
    :param access_token:
    :param the expected role of the user:
    :return the user JSON object or False if there is no token or the role is not matched:
    """
    return {
        "login": "kira390",
        "password": "123456",
        "role": "admin"
    }