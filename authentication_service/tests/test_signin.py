import unittest

from mockupdb import go, MockupDB, OpMsg
from mockupdb._bson import ObjectId as mockup_oid

from authentication_service.authservice import app
from authentication_service.common import generate_access_token

USER = {
        "_id": mockup_oid("5b37fff8bbf300b7ef185042"),
        "login": "kira390@gmail.com",
        "password": "123456",
        "role": "admin"
    }

CLIENT = {
    "_id" : mockup_oid("5b37fff8bbf300b7ef185045"),
    "client_id" : "midleware1",
    "client_secret" : "1sfg135df1d32fsdf489d7q6sdq6s4d"
}


class SignInTest(unittest.TestCase):
    def setUp(self):
        """
        Prepare the test envirement.
        start the server to mockup the database
        """
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()
        app.testing = True
        app.config['MONGO_URI'] = self.server.uri
        self.app = app.test_client()

    def tearDown(self):
        """shuts down the mockupDB server"""
        self.server.stop()

    def test_signin_invalid_client(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com", "password": "123456"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice")
        CLIENT_REQ = OpMsg({
            "find": "clients",
            "filter": {"client_id": "midleware1", "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice")

        future = go(self.app.post, '/auth/signin', json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [USER]})
        request = self.server.receives(CLIENT_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': []})

        self.assertEqual(future().status_code, 400)

    def test_signin_invalid_user(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com", "password": "123456"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice")

        future = go(self.app.post, '/auth/signin', json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': []})

        self.assertEqual(future().status_code, 400)

    def test_signin_valid_user(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com", "password": "123456"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice")
        CLIENT_REQ = OpMsg({
            "find": "clients",
            "filter": {"client_id": "midleware1", "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice")

        future = go(self.app.post,'/auth/signin', json={
                            "userID": '',
                            "login": "kira390@gmail.com",
                            "password": "123456",
                            "client_id": "midleware1",
                            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
                        })
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [USER]})
        request = self.server.receives(CLIENT_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [CLIENT]})

        self.assertEqual(future().status_code, 200)

    def test_signin_get_users(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {},
            "projection": {"password": 0},
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice")
        user = {
            "_id": "5b37fff8bbf300b7ef185042",
            "login": "kira390@gmail.com",
            "password": "123456",
            "role": "admin"
        }

        access_token = generate_access_token(
            user=user,
            pivate_key=app.config['PRIVATE_KEY'],
            auth_host=app.config['AUTH_HOST'],
            token_ttl=app.config['TOKEN_TTL'],
            auth_algo=app.config['AUTH_ALGO']
        )
        headers = {'Authorization': 'Bearer {}'.format(access_token['access_token'])}
        future = go(self.app.get, '/auth/signin', headers=headers)
        request = self.server.receives(USER_REQ, timeout=60)
        request.ok(cursor={'id': 0, 'firstBatch': [USER]})

if __name__ == '__main__':
    unittest.main
