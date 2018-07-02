from flask_restful import Resource, reqparse
from geopy import distance
from pymongo import MongoClient


class BaseShop(Resource):
    def __init__(self, app):
        self.database = MongoClient(app.config['MONGO_URI'])[app.config['MONGO_DBNAME']]
        self.auth_host = app.config['AUTH_HOST']
        self.token_ttl = app.config['TOKEN_TTL']
        self.auth_algo = app.config['AUTH_ALGO']
        self.public_key = app.config['PUBLIC_KEY']

        # Parses arguments to check if there is any location to filter on.
        self.location_parser = reqparse.RequestParser()
        self.location_parser.add_argument('latitude', type=float)
        self.location_parser.add_argument('longitude', type=float)

        # Parses arguments to chack if there is a shop object available.
        self.shop_parser = reqparse.RequestParser()
        self.shop_parser.add_argument('_id', type=str)
        self.shop_parser.add_argument('name', type=str)
        self.shop_parser.add_argument('address', type=str)
        self.shop_parser.add_argument('longitude', type=float)
        self.shop_parser.add_argument('latitude', type=float)

    def sort_shops_by_distance(self, shops, location):
        """
        This Method sorts a list of shop by distance from a location
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