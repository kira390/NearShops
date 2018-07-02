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
        shops = self.database['shops'].find({"dislikers.login": {"$eq": user['login']}}, {"dislikers":0, "likers":0})
        result = []
        for shop in shops:
            shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
            result.append(shop)
        if args["latitude"] and args["latitude"]:
            location = (args["longitude"], args["latitude"])
            result = self.sort_shops_by_distance(result, location)
        return result

    def post(self):
        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        args = self.shop_parser.parse_args()
        try:
            shop_id = ObjectId(args["_id"])
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        shops = self.database['shops']
        opp = {
            "$addToSet": {"dislikers": {"login":user["login"], "timestamp":time.time()}}
        }
        counter = shops.count({
            "$and": [
                {"_id": shop_id},
                {"likers": user['login']},
            ]
        })
        if counter > 0:
            abort(400, message="user likes this shop")
        status = shops.update_one({"_id": shop_id}, opp)

        if status.matched_count == 0:
            abort(400, message="shop_id doesn't exist")
        elif status.modified_count == 0:
            abort(400, message="Update failed")
        return {"id": shop_id}, 201

    def delete(self):
        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        args = self.shop_parser.parse_args()
        shop_id = args["_id"]
        shops = self.database['shops']
        opp = {
            "$pull": {"dislikers": {"login":user['login']}}
        }
        try:
            status = shops.update_one({"_id": ObjectId(shop_id)}, opp)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if status.matched_count == 0:
            abort(400, message="shop_id doesn't exist")
        elif status.modified_count == 0:
            abort(400, message="unliking shop failed")
        return '', 204