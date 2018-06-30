import json

from bson import ObjectId, errors, json_util
from flask import request
from flask_restful import Resource, abort

from shop_service.common import MONGO, is_authenticated, SHOP_PARSER


class Shop(Resource):
    """
    This Class represents the Shop resource.
    it handles operations on a specific shop given id given in arguments
    :urls /shops/<shop_id>
    :operations GET, PUT, DELETE
    """
    def get(self, shop_id):
        is_authenticated(request)
        try:
            shop = MONGO['shops'].find_one({"_id": ObjectId(shop_id)},{"dislikers":0, "likers":0})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if shop is None:
            abort(400, message="shop_id doesn't exist")
        shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
        return shop

    def delete(self, shop_id):
        is_authenticated(request,role='admin')
        shops = MONGO['shops']
        try:
            shop_counter = shops.count({"_id": ObjectId(shop_id)})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if shop_counter == 0:
            abort(400, message="Invalid Shop Id")
        else:
            shops.delete_one({"_id": ObjectId(shop_id)})
            if shops.count({"_id": ObjectId(shop_id)}) == shop_counter-1:
                return '',204
            else:
                abort(400, message="Delete faild")

    def put(self, shop_id):
        is_authenticated(request, role='admin')
        args=SHOP_PARSER.parse_args()
        shop = {
            "_id": ObjectId(args["_id"]),
            "name": args["name"],
            "address": args["address"],
            "longitude": args["longitude"],
            "latitude": args["latitude"]
        }
        shops = MONGO['shops']
        try:
            shop_counter = shops.count({"_id": ObjectId(shop_id)})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if shop_counter == 0:
            abort(400, message="Invalid Shop Id")
        else:
            status = shops.update_one({"_id": ObjectId(shop_id)}, shop)
            if status.matched_count==1 and status.modified_count==1:
                return shop, 201
            else:
                abort(400, message="Update faild")