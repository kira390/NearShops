from flask_restful import Resource
import json

from bson import json_util
from flask_restful import abort, reqparse
from pymongo import MongoClient


class Auth(Resource):
    """
    This class serves as parent class for the SignIn and SignUp resources
    it defines the methodes and atributes that both shared
    """
    def __init__(self, app):
        self.database= MongoClient(app.config['MONGO_URI'])[app.config['MONGO_DBNAME']]
        self.pivate_key = app.config['PRIVATE_KEY']
        self.auth_host = app.config['AUTH_HOST']
        self.token_ttl = app.config['TOKEN_TTL']
        self.auth_algo = app.config['AUTH_ALGO']
        self.public_key = app.config['PUBLIC_KEY']
        self.user_parser = reqparse.RequestParser()
        self.user_parser.add_argument('userID', required=True, type=str)
        self.user_parser.add_argument('login', required=True, type=str)
        self.user_parser.add_argument('password', required=True, type=str)
        self.user_parser.add_argument('client_id', required=True, type=str)
        self.user_parser.add_argument('client_secret', required=True, type=str)

    def user_exists(self, login):
        """
        This method checks if a user exist
        :param login:
        :return the user objec or False:
        """
        user = self.database['users'].find_one(
            {
                "login": login,
            }
        )
        if user is None:
            return False
        else:
            user["_id"] = json.loads(json_util.dumps(user["_id"]))["$oid"]
            return user

    def client_exists(self, client_id, client_secret):
        """
        This method checks if a client exists
        :param client_id:
        :param client_secret:
        :return the Client object or False:
        """
        client = self.database['clients'].find_one(
            {
                "client_id": client_id,
                "client_secret": client_secret
            }
        )
        if client is None:
            return False
        else:
            client["_id"] = json.loads(json_util.dumps(client["_id"]))["$oid"]
            return client
