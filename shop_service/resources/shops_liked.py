import json
import time

from bson import json_util, errors, ObjectId
from flask import request
from flask_restful import Resource, abort

from shop_service.common import LOCATION_PARSER,SHOP_PARSER,MONGO
from shop_service.common import is_authenticated, sort_shops_by_distance


class ShopsLiked(Resource):
    """
    This Class represents the Liked Shops resource.
    it handles operations on liked shops lists
    :urls /shops/liked, /shops/liked
    :operations GET, POST, DELETE
        - GET accepts two arguments for longitude and latitude
    """
    def get(self):
        user = is_authenticated(request)
        args = LOCATION_PARSER.parse_args()
        shops = MONGO['shops'].find({"likers":user["login"]},{"dislikers":0, "likers":0})
        result = []
        for shop in shops:
            shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
            result.append(shop)
        if args["latitude"] and args["latitude"]:
            location = (args["longitude"], args["latitude"])
            result = sort_shops_by_distance(result,location)
        return result

    def post(self):
        user = is_authenticated(request)
        args = SHOP_PARSER.parse_args()
        try:
            shop_id = ObjectId(args["_id"])
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        shops = MONGO['shops']
        opp = {
            "$addToSet": {"likers": user["login"]}
        }
        counter=shops.count({
            "$and":[
                {"_id": shop_id},
                {"dislikers.login":{"$eq":user['login']}},
                {"dislikers.timestamp": {"$gte": time.time() - 7200}}
            ]
        })
        if counter > 0:
            abort(400, message="user dislikes this shop")
        status = shops.update_one({"_id": shop_id}, opp)

        if status.matched_count == 0:
            abort(400, message="shop_id doesn't exist")
        elif status.modified_count == 0:
            abort(400, message="Update faild")
        return {"id": shop_id}, 201

    def delete(self):
        user = is_authenticated(request)
        args = SHOP_PARSER.parse_args()
        shop_id = args["_id"]
        shops = MONGO['shops']
        opp = {
            "$pull": {"likers": user["login"]}
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
