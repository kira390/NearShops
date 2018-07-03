import json
import time

from bson import ObjectId, json_util, errors
from flask_restful import Resource, reqparse, abort
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

    def find_shops(self, id=None, liked=False, disliked=False, user_login=None, longitude=None, latitude=None):
        shops = self.database["shops"]
        if id is not None:
            shop = shops.find_one({"_id": ObjectId(id)},{"dislikers":0, "likers":0})
            if shop:
                shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
                return shop
            else:
                abort(400, message="this Shop doesn't exist")
        if liked is True:
            if user_login is None: raise ValueError("can't find user_id argument")
            req = {"likers":user_login}
        elif disliked is True:
            if user_login is None: raise ValueError("can't find user_id argument")
            req = {
                "$and":[
                    {"dislikers.login": {"$eq": user_login}},
                    {"dislikers.timestamp": {"$gte": time.time() - 7200}}
                ]
            }
        else:
            req = {
                "$or": [
                    {"dislikers.login": {"$ne": user_login}},
                    {"dislikers.timestamp": {"$lte": time.time() - 7200}},
                    {"likers": {"$ne": user_login}},
                    {"likers": None,"disliker":None}
                ]
            }
        shop_list = shops.database['shops'].find(req, {"dislikers": 0, "likers": 0})
        result=[]
        for shop in shop_list:
            shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
            result.append(shop)
        if latitude and longitude:
            location = (longitude, latitude)
            result = self.sort_shops_by_distance(result,location)
        return result

    def add_shop(self,name,address,latitude,longitude):
        shops = self.database["shops"]
        shop_pattern = {
            "name": name,
            "address": address,
            "longitude": longitude,
            "latitude": latitude
        }
        shop_search_pattern = {"$or":
            [
                {
                    "name": name,
                    "address": address,
                    "longitude": longitude,
                    "latitude": latitude
                },
                {
                    "longitude": longitude,
                    "latitude": latitude
                }
            ]
        }
        shop = shops.find_one(shop_search_pattern)
        if shop:
            if shop["name"] == name:
                abort(400, message="this Shop already exist")
            else:
                abort(400, message="An other shop exist in the same location")
        shops.insert_one(shop_pattern).inserted_id
        shop = shops.find_one(shop_pattern)
        if not shop:
            abort(400, message="Failed to add the shop")
        shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
        return shop

    def update_shop(self, shop_id, name, address, longitude, latitude):
        try:
            shop_id = ObjectId(shop_id)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        shop = {
            "_id": shop_id,
            "name": name,
            "address": address,
            "longitude": longitude,
            "latitude": latitude
        }
        shops = self.database['shops']
        shop_counter = shops.find_one({"_id": shop_id})
        if not shop_counter:
            abort(400, message="This shop doesn't exist")
        else:
            status = shops.update_one({"_id": shop_id}, shop)
            if status.matched_count==1 and status.modified_count==1:
                return shop, 201
            else:
                abort(400, message="Update faild")

    def delete_shop(self, shop_id):
        shops = self.database['shops']
        try:
            shop_counter = shops.count({"_id": ObjectId(shop_id)})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if shop_counter == 0:
            abort(400, message="Invalid Shop Id")
        else:
            shops.delete_one({"_id": ObjectId(shop_id)})
            if shops.count({"_id": ObjectId(shop_id)}) == shop_counter - 1:
                return ''
            else:
                abort(400, message="Delete faild")

    def like_dislike_shop(self,user_login, shop_id, dislike=False):
        try:
            shop_id = ObjectId(shop_id)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        shops = self.database['shops']

        user_like = shops.find_one({
            "$and": [
                {"_id": shop_id},
                {"likers": user_login},
            ]
        })
        if user_like:
            abort(400, message="user already likes this shop")
        user_dislike = shops.find_one({
            "$and": [
                {"_id": shop_id},
                {"dislikers.login": {"$eq": user_login}},
                {"dislikers.timestamp": {"$gte": time.time() - 7200}},
            ]
        })
        if user_dislike :
            abort(400, message="user already dislikes this shop")
        if dislike:
            opp = {"$addToSet": {"dislikers": {"login": user_login, "timestamp": time.time()}}}
        else:
            opp = {"$addToSet": {"likers": user_login}}

        status = shops.update_one({"_id": shop_id}, opp).modified_count
        if status != 1:
            return abort(400, message="like or dislike operation failed")

        return {"id":json.loads(json_util.dumps(shop_id))["$oid"]}

    def unlik_undislike_shop(self, shop_id, user_login, undislike=False):
        shops = self.database['shops']
        if undislike:
            opp = {"$pull": {"dislikers": {"login": user_login}}}
        else:
            opp = {"$pull": {"likers": user_login}}
        try:
            status = shops.update_one({"_id": ObjectId(shop_id)}, opp)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if status.matched_count == 0:
            abort(400, message="This Shop doesn't exist")
        elif status.modified_count == 0:
            abort(400, message="Unliking/Undisliking shop failed")
        return ''

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