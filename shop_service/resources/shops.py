import json
import time

from bson import ObjectId, errors, json_util
from flask import request
from flask_restful import Resource, abort

from shop_service.common import MONGO, SHOP_PARSER, LOCATION_PARSER
from shop_service.common import is_authenticated, sort_shops_by_distance


class Shops(Resource):
    """
    This Class represents the Shops resource.
    it handles operations on shops lists
    :urls /shops, /shops/
    :operations GET, POST
        - GET accepts two arguments for longitude and latitude
    """
    def get(self):
        user = is_authenticated(request)
        args = LOCATION_PARSER.parse_args()
        shops = MONGO['shops'].find({
            "$or": [
                {"dislikers.login":{"$ne": user['login']}},
                {"dislikers.timestamp":{"$lte": time.time()-7200}},
                {"likers":{"$ne": user['login']}}
            ]
        },{"dislikers":0, "likers":0})
        result = []
        for shop in shops:
            shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
            result.append(shop)
        if args["latitude"] and args["latitude"]:
            location = (args["longitude"], args["latitude"])
            shops = sort_shops_by_distance(result,location)
        return shops

    def post(self):
        is_authenticated(request,role='admin')
        args = SHOP_PARSER.parse_args()
        shop = {
            "_id": ObjectId(args["_id"]),
            "name": args["name"],
            "address": args["address"],
            "longitude": args["longitude"],
            "latitude": args["latitude"]
        }
        shops = MONGO['shops']
        shop_id = args["_id"]
        try:
            shop_counter = shops.count({"_id": ObjectId(shop_id)})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if shop_counter != 0:
            abort(400, message="this Shop already exist")
        else:
            status = shops.insert_one(shop).inserted_id
            if status:
                abort(400, message="Update faild")
            else:
                return shop, 201