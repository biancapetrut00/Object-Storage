from object_storage.test.functional.api import base
import requests

class UserTests(base.BaseTestCase):
    def test_create_user(self):
        pass

    def test_get_users(self):
        url = self._get_url("/users")
        r = requests.get(url)
        #r = requests.get("127.0.0.1/users")
        #self.assertEqual(r.status_code, 200)
        print(r)