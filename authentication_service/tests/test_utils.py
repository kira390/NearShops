import unittest

from authentication_service.authservice import app


class TestUtils(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_unauthenticated_access(self):
        response = self.app.delete('/auth/signup', json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        self.assertEquals(response.status_code,401)

    def test_invalid_token(self):
        headers = {'Authorization': 'Bearer {}'.format('access_token')}
        response = self.app.delete('/auth/signup',headers=headers , json={
            "userID": '',
            "login": "kira390@gmail.com",
            "password": "123456",
            "client_id": "midleware1",
            "client_secret": "1sfg135df1d32fsdf489d7q6sdq6s4d"
        })
        self.assertEquals(response.status_code,400)

if __name__ == '__main__':
    unittest.main
