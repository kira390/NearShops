import time
import unittest

import jwt
from mockupdb import go, MockupDB, OpMsg
from mockupdb._bson import ObjectId as mockup_oid

from shopservice import app


def mock_access_token():
    """
    This function generates a fake JWT token
    :return the generated access token:
    """
    with open("private.pem", 'rb') as f:
        private_key = f.read()
    payload = {
        "iss": "localhost",
        "exp": time.time() + 1800,
        "user": {"_id" : "5b3a7297d2e5ce5bbd3d0121", "login" : "kira390@gmail.com", "password" : "123456", "role" : "admin"}
    }
    access_token = jwt.encode(payload, private_key, algorithm="RS256")
    return {
        "access_token": access_token.decode(),
        "token_type": "JWT",
        "expire_in": 1800
    }

SHOP_RESULT = { "_id" : mockup_oid("5b37fff8bbf300b7ef185042"), "name" : "Restaurant Zayna", "address" : "104 Boulevard Omar Al Khiam, Casablanca 20850", "longitude" : 33.577321, "latitude" : -7.607404}
SHOP_REQ={
            "name" : "Restaurant Zayna",
            "address" : "104 Boulevard Omar Al Khiam, Casablanca 20850",
            "longitude" : 33.577321,
            "latitude" : -7.607404
        }

class TestShop(unittest.TestCase):

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
        self.token = mock_access_token()['access_token']
        self.auth_header = {'Authorization': 'Bearer {}'.format(self.token)}

    def tearDown(self):
        self.server.stop()

    def test_get_shop_shops(self):
        future = go(self.app.get, '/shops', headers=self.auth_header)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 200)

        future = go(self.app.get, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': [SHOP_RESULT]})
        self.assertEqual(future().status_code,200)

    def test_post_shops(self):
        future = go(self.app.post, '/shops', headers=self.auth_header, json=SHOP_REQ)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        request = self.server.receives()
        request.ok({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True})
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': [SHOP_RESULT]})
        self.assertEqual(future().status_code, 201)

    def test_delete_shop_valid(self):
        future = go(self.app.delete, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': [SHOP_RESULT]})
        request = self.server.receives()
        request.ok()
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 204)

    def test_put_shop_valid(self):
        future = go(self.app.put, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header, json=SHOP_REQ)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': [SHOP_RESULT]})
        request = self.server.receives()
        request.ok({'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True})
        self.assertEqual(future().status_code, 201)

    def test_put_shop_noshop_given(self):
        future = go(self.app.put, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header)
        self.assertEqual(future().status_code, 400)

    #Those methodes bellow do common test for all operations

    def test_notoken(self):
        future = go(self.app.get, '/shops/5b3a7297d2e5ce5bbd3d0121')
        self.assertEqual(future().status_code, 401)

        future = go(self.app.put, '/shops/5b3a7297d2e5ce5bbd3d0121')
        self.assertEqual(future().status_code, 401)

        future = go(self.app.delete, '/shops/5b3a7297d2e5ce5bbd3d0121')
        self.assertEqual(future().status_code, 401)

        future = go(self.app.get, '/shops')
        self.assertEqual(future().status_code, 401)

        future = go(self.app.post, '/shops')
        self.assertEqual(future().status_code, 401)

    def test_invalid_token(self):
        headers = {'Authorization': 'Bearer invalid_token'}
        future = go(self.app.get, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=headers)
        self.assertEqual(future().status_code, 400)

        future = go(self.app.put, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=headers)
        self.assertEqual(future().status_code, 400)

        future = go(self.app.delete, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=headers)
        self.assertEqual(future().status_code, 400)

        future = go(self.app.get, '/shops', headers=headers)
        self.assertEqual(future().status_code, 400)

        future = go(self.app.post, '/shops', headers=headers)
        self.assertEqual(future().status_code, 400)

    def test_shop_notfound(self):
        future = go(self.app.get, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 400)

        future = go(self.app.put, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header, json=SHOP_REQ)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 400)

        future = go(self.app.delete, '/shops/5b3a7297d2e5ce5bbd3d0121', headers=self.auth_header)
        request = self.server.receives()
        request.ok(cursor={'id': 0, 'firstBatch': []})
        self.assertEqual(future().status_code, 400)

    def test_invalid_shop_id(self):
        future = go(self.app.get, '/shops/invalidid', headers=self.auth_header)
        self.assertEqual(future().status_code, 400)

        future = go(self.app.put, '/shops/invalidid', headers=self.auth_header)
        self.assertEqual(future().status_code, 400)

        future = go(self.app.delete, '/shops/invalidid', headers=self.auth_header)
        self.assertEqual(future().status_code, 400)



if __name__ == '__main__':
    unittest.main()