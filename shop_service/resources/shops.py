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

        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)

        args = self.location_parser.parse_args()
        shops = self.database['shops'].find({
            "$or": [
                {"dislikers.login":{"$ne": user['login']}},
                {"dislikers.timestamp":{"$lte": time.time()-7200}},
                {"likers":{"$ne": user['login']}}
            ]
        },{"dislikers":0, "likers":0})
        result = []
        print("loool")
        for shop in shops:
            shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
            result.append(shop)
        if args["latitude"] and args["latitude"]:
            location = (args["longitude"], args["latitude"])
            result = self.sort_shops_by_distance(result,location)
        return result

    def post(self):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo, role='admin')
        args = self.shop_parser.parse_args()
        shop = {
            "name": args["name"],
            "address": args["address"],
            "longitude": args["longitude"],
            "latitude": args["latitude"]
        }
        shops = self.database['shops']
        if shops.find_one(shop):
            abort(400, message="this Shop already exist")
        else:
            status = shops.insert_one(shop).inserted_id
            if status:
                abort(400, message="Update faild")
            else:
                shop["_id"]=status
                return shop, 201