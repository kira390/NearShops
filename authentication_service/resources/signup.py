import json

from bson import ObjectId, json_util
from flask import request
from flask_restful import abort
from pymongo.errors import DuplicateKeyError

from common import Auth, is_authenticated, isValidEmail


class SignUp(Auth):
    """
        This Class handles the SignUp process.
        it handles user SignUp and update and allow the admins to delete users
        :urls /auth/signup
        :operations GET, POST
    """
    def __init__(self, **kwargs):
        app=kwargs["app"]
        Auth.__init__(self, app)

    def post(self):
        args = self.user_parser.parse_args()
        if not isValidEmail(args["login"]):
            abort(400, message='Invalid Email Address')
        login = args['login']
        password = args['password']
        client_id = args['client_id']
        client_secret = args['client_secret']

        if not self.client_exists(client_id, client_secret):
            abort(400, message='Client Invalid')

        users = self.database["users"]
        user = {
            "login": login,
            "password": password,
            "role": "regular"
        }
        if self.user_exists(login):
            abort(400, message='User Alredy exists')
        try:
            status = users.insert_one(user).inserted_id
        except DuplicateKeyError:
            abort(400, message='User Alredy exists')

        del user["password"]
        user["_id"]=json.loads(json_util.dumps(status))["$oid"]
        return user, 201

    def put(self):
        args = self.user_parser.parse_args()
        user = is_authenticated(request, self.public_key, self.auth_host, self.auth_algo)
        if not isValidEmail(args["login"]):
            abort(400, message='Invalid Email Address')
        login = args['login']
        password = args['password']
        if user["login"] == login or user["role"] == "admin":
            old_user = self.user_exists(login)
            if not old_user :
                abort(400, message="User doesn't exists")
            users = self.database["users"]
            user['_id']=ObjectId(old_user["_id"])
            status = users.replace_one({"login":user["login"]}, user)
            if status.matched_count == 1 and status.modified_count == 1:
                del user["password"]
                return user, 201
            else:
                abort(400, message="Update failed")

    def delete(self):

        is_authenticated(request, self.public_key, self.auth_host, self.auth_algo, role='admin')
        args = self.user_parser.parse_args()
        users = self.database['users']
        old_user=self.user_exists(args["login"])
        if not old_user:
            abort(400, message="User doesn't exist")
        else:
            user_id = ObjectId(old_user["_id"])
            users.delete_one({"_id": user_id})
            if not self.user_exists(args["login"]):
                return '', 204
            else:
                abort(400, message="Delete failed")


