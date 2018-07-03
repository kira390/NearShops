import json

from bson import ObjectId, errors, json_util
from flask import request
from flask_restful import abort

from common import BaseShop, is_authenticated


class Shop(BaseShop):
    """
    This Class represents the Shop resource.
    it handles operations on a specific shop given id given in arguments
    :urls /shops/<shop_id>
    :operations GET, PUT, DELETE
    """
    def __init__(self, **kwargs):
        app = kwargs["app"]
        BaseShop.__init__(self, app)

    def get(self, shop_id):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        return self.find_shops(id=shop_id)

    def delete(self, shop_id):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo,role='admin')
        return self.delete_shop(shop_id), 204

    def put(self, shop_id):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo, role='admin')
        args=self.shop_parser.parse_args()
        return self.update_shop(shop_id, args["name"], args["address"], args["longitude"], args["latitude"])