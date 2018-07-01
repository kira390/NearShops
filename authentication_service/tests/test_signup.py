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
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()
        app.testing = True
        app.config['MONGO_URI'] = self.server.uri
        self.app = app.test_client()

    def tearDown(self):
        self.server.stop()

    def test_delete_user(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com"},
            "limit": 1,
            "singleBatch": True,
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
        future = go(self.app.delete, '/auth/signup', headers=headers, json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [USER]})
        self.server.receives().ok()
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': []})

        self.assertEqual(future().status_code, 204)

    def test_nonadmin_delete(self):
        user = {
            "_id": "5b37fff8bbf300b7ef185042",
            "login": "kira390@gmail.com",
            "password": "123456",
            "role": "regular"
        }
        access_token = generate_access_token(
            user=user,
            pivate_key=app.config['PRIVATE_KEY'],
            auth_host=app.config['AUTH_HOST'],
            token_ttl=app.config['TOKEN_TTL'],
            auth_algo=app.config['AUTH_ALGO']
        )
        headers = {'Authorization': 'Bearer {}'.format(access_token['access_token'])}
        future = go(self.app.delete, '/auth/signup', headers=headers, json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })

        self.assertEqual(future().status_code, 401)

    def test_delete_nonexisting_user(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com"},
            "limit": 1,
            "singleBatch": True,
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
        future = go(self.app.delete, '/auth/signup', headers=headers, json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': []})

        self.assertEqual(future().status_code, 400)

    def test_signup_valid_client_success(self):
        CLIENT_REQ = OpMsg({
            "find": "clients",
            "filter": {"client_id": "midleware1", "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice"
        )

        future = go(self.app.post, '/auth/signup', json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })

        request = self.server.receives(CLIENT_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [CLIENT]})
        self.server.receives().ok({"_id":USER["_id"]})
        self.assertEqual(future().status_code, 201)

    def test_signup_create_existing_user(self):
        CLIENT_REQ = OpMsg({
            "find": "clients",
            "filter": {"client_id": "midleware1", "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice"
        )

        future = go(self.app.post, '/auth/signup', json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })

        request = self.server.receives(CLIENT_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [CLIENT]})
        self.server.receives().command_err(11000,"failed")
        self.assertEqual(future().status_code, 400)

    def test_signup_with_invalid_client(self):
        CLIENT_REQ = OpMsg({
            "find": "clients",
            "filter": {"client_id": "midleware1", "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"},
            "limit": 1,
            "singleBatch": True,
            "$db": "authservice",
            "$readPreference": {"mode": "primaryPreferred"}},
            namespace="authservice"
        )

        future = go(self.app.post, '/auth/signup', json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })

        request = self.server.receives(CLIENT_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 400)

    def test_signup_with_invalid_email(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com"},
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
            namespace="authservice"
        )

        future = go(self.app.post, '/auth/signup', json={
            "userID": '',
            "login": "kira390",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        self.assertEqual(future().status_code, 400)

    def test_update_invalid_email(self):
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
        future = go(self.app.put, '/auth/signup', headers=headers, json={
            "userID": '',
            "login": "kira390",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        self.assertEqual(future().status_code, 400)

    def test_update_invalid_user(self):
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
        future = go(self.app.put, '/auth/signup', headers=headers, json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        self.server.receives().ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 400)

    def test_update_valid(self):
        USER_REQ = OpMsg({
            "find": "users",
            "filter": {"login": "kira390@gmail.com"},
            "limit": 1,
            "singleBatch": True,
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
        future = go(self.app.put, '/auth/signup', headers=headers, json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        request = self.server.receives(USER_REQ)
        request.ok(cursor={'id': 0, 'firstBatch': [USER]})
        self.server.receives().ok()
        self.assertEqual(future().status_code, 400)

if __name__ == '__main__':
    unittest.main
