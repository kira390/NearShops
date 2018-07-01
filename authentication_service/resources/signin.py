import json

from bson import json_util
from flask import request
from flask_restful import abort

from authentication_service.common import Auth,generate_access_token, is_authenticated


class SignIn(Auth):
    """
        This Class handles the SignIn process.
        it handles user authentication and allow the admins to list users
        :urls /auth/signin
        :operations GET, POST
    """
    def __init__(self, **kwargs):
        app = kwargs["app"]
        Auth.__init__(self, app)

    def user_exists(self, login, password):
        """
                This method checks if a user exist
                :param login:
                :return the user objec or False:
                """
        user = self.database['users'].find_one(
            {
                "login": login,
                "password": password
            }
        )
        if user is None:
            return False
        else:
            user["_id"] = json.loads(json_util.dumps(user["_id"]))["$oid"]
            return user

    def post(self):
        args = self.user_parser.parse_args()
        login = args['login']
        password = args['password']
        client_id = args['client_id']
        client_secret = args['client_secret']
        user = self.user_exists(login, password)
        if not user:
            abort(400,message='User Invalid',user=user)

        if not self.client_exists(client_id, client_secret):
            abort(400,message='Client Invalid')

        access_token = generate_access_token(user,  self.pivate_key, self.auth_host, self.token_ttl, self.auth_algo)
        return access_token

    def get(self):
        is_authenticated(request, public_key=self.public_key, auth_host=self.auth_host, auth_algo=self.auth_algo, role='admin')
        users = self.database['users']
        result=[]
        for user in users.find({},{"password":0}):
            user["_id"] = json.loads(json_util.dumps(user["_id"]))["$oid"]
            result.append(user)
        return result