from datetime import datetime
import json


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

    def find_unliked_undisliked_shops(self, user_login):
        if user_login is None:
            raise ValueError("can't find user_id argument")
        shops = self.database["shops"]
        tmp = []
        for disliker in self.find_disliked_shops(user_login):
            tmp.append(disliker["_id"])
        shop_list = []
        for shop in shops.find({"likers": {"$ne": user_login}}, {"likers": 0}):
            if shop["_id"] not in tmp:
                shop_list.append(shop)
        return shop_list

    def find_liked_shops(self, user_login):
        shops = self.database["shops"]
        if user_login is None:
            raise ValueError("can't find user_id argument")
        return shops.find({"likers": user_login}, {"likers": 0})

    def find_disliked_shops(self, user_login):
        if user_login is None:
            raise ValueError("can't find user_id argument")
        shops = self.database["shops"]
        dislikers = self.database["dislikers"]
        tmp = []
        for disliker in dislikers.find({"login": user_login}):
            print(json_util.dumps(disliker))
            tmp.append(disliker["shop_id"])
        return shops.find({"_id":{"$in": tmp}}, {"likers": 0})

    def find_shops(self, shop_id=None, liked=False, disliked=False, user_login=None, longitude=None, latitude=None):
        shops = self.database["shops"]
        if shop_id is not None:
            try:
                shop_id = ObjectId(shop_id)
            except errors.InvalidId:
                abort(400, message="Invalid Shop Id")
            shop = shops.find_one({"_id": ObjectId(shop_id)},{"likers":0})
            if not shop:
                abort(400, message="this Shop doesn't exist")
            shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
            return shop
        if liked is True:
            shop_list = self.find_liked_shops(user_login)
        elif disliked is True:
            shop_list = self.find_disliked_shops(user_login)
        else:
            shop_list = self.find_unliked_undisliked_shops(user_login)
        result = []
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
        shops.insert_one(shop_pattern)
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
            status = shops.replace_one({"_id": shop_id}, shop)
            if status.matched_count==1 and status.matched_count==1:
                shop["_id"] = json.loads(json_util.dumps(shop["_id"]))["$oid"]
                return shop
            elif status.modified_count==0:
                abort(200, message="Nothing to change")
            else:
                abort(400, message="Update failed")

    def delete_shop(self, shop_id):
        shops = self.database['shops']
        try:
            shop = shops.find_one({"_id": ObjectId(shop_id)})
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if not shop:
            abort(400, message="Shop not found")
        else:
            status = shops.delete_one({"_id": ObjectId(shop_id)}).raw_result
            print(str(status))
            if not shops.find_one({"_id": ObjectId(shop_id)}):
                return ''
            else:
                abort(400, message="Delete failed")

    def like_dislike_shop(self,user_login, shop_id, dislike=False):
        try:
            shop_id = ObjectId(shop_id)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        shops = self.database['shops']
        liker = shops.find_one({"$and":[{"_id": shop_id},{"likers": user_login}]})
        disliker = self.database.dislikers.find_one({"$and":[{"shop_id": shop_id},{"user_login":user_login}]})
        if liker:
            abort(400, message="user already likes this shop")
        elif disliker:
            abort(400, message="user already dislikes this shop")
        if dislike:
            opp = {"shop_id": shop_id, "login": user_login, "timestamp": datetime.now() }
            status = self.database["dislikers"].insert_one(opp).inserted_id
            if not status:
                abort(400, message="dislike operation failed")
        else:
            opp = {"$addToSet": {"likers": user_login}}
            status = shops.update_one({"_id": shop_id}, opp).modified_count
            if status != 1:
                abort(400, message="like operation failed")

        return {"id":json.loads(json_util.dumps(shop_id))["$oid"]}

    def unlik_undislike_shop(self, shop_id, user_login, undislike=False):
        shops = self.database['shops']
        try:
            shop_id = ObjectId(shop_id)
        except errors.InvalidId:
            abort(400, message="Invalid Shop Id")
        if undislike:
            status = self.database["dislikers"].delete_one({"shop_id": shop_id}).deleted_count
        else:
            status = shops.update_one({"_id": shop_id}, {"$pull": {"likers": user_login}}).modified_count
        if status == 0:
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