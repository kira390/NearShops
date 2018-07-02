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
        try:
            shop = self.database['shops'].find_one({"_id": ObjectId(shop_id)},{"dislikers":0, "likers":0})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if shop is None:
            abort(400, message="shop_id doesn't exist")
        shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
        return shop

    def delete(self, shop_id):
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo,role='admin')
        shops = self.database['shops']
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
        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo, role='admin')
        args=self.shop_parser.parse_args()
        try:
            shop_id = ObjectId(shop_id)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        shop = {
            "_id": shop_id,
            "name": args["name"],
            "address": args["address"],
            "longitude": args["longitude"],
            "latitude": args["latitude"]
        }
        shops = self.database['shops']
        shop_counter = shops.count({"_id": shop_id})
        if shop_counter == 0:
            abort(400, message="Invalid Shop Id")
        else:
            status = shops.update_one({"_id": ObjectId(shop_id)}, shop)
            if status.matched_count==1 and status.modified_count==1:
                return shop, 201
            else:
                abort(400, message="Update faild")