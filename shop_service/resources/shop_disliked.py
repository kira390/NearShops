import json
import time

from bson import json_util, errors, ObjectId
from flask import request
from flask_restful import Resource, abort

from common import is_authenticated, BaseShop


class ShopsDisliked(BaseShop):
    """
    This Class represents the disliked Shops resource.
    it handles operations on disliked shops lists
    :urls /shops/disliked, /shops/disliked
    :operations GET, POST, DELETE
        - GET accepts two arguments for longitude and latitude
    """
    def __init__(self, **kwargs):
        app = kwargs["app"]
        BaseShop.__init__(self, app)

    def get(self):
        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        args = self.location_parser.parse_args()
        return self.find_shops(disliked=True, user_login=user['login'], longitude=args['longitude'], latitude=args['latitude'])

    def post(self):
        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        args = self.shop_parser.parse_args()

        return self.like_dislike_shop(user["login"], args["_id"], dislike=True), 201

    def delete(self):
        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        args = self.shop_parser.parse_args()
        return self.unlik_undislike_shop(args["_id"], user["login"],undislike=True), 204