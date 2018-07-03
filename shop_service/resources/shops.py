import json
import time

from bson import json_util
from flask import request
from flask_restful import abort

from common import is_authenticated, BaseShop


class Shops(BaseShop):
    """
    This Class represents the Shops resource.
    it handles operations on shops lists
    :urls /shops, /shops/
    :operations GET, POST
        - GET accepts two arguments for longitude and latitude
    """
    def __init__(self, **kwargs):
        app = kwargs["app"]
        BaseShop.__init__(self, app=app)

    def get(self):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo, role='admin')
        args = self.location_parser.parse_args()
        return self.find_shops(longitude=args["longitude"],latitude=args["latitude"])

    def post(self):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo, role='admin')
        args = self.shop_parser.parse_args()
        return self.add_shop(args["name"], args["address"], args["longitude"], args["latitude"]), 201