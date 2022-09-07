from object_storage.test.functional.api import base
from object_storage.db import models
import requests
import json

class UserTests(base.BaseTestCase):
    token = None

    def test_create_user(self):
        username = "new_user"
        password = "new_pass"
        user = self._create_test_user(username, password)
        self.assertEqual(user['name'], username)
        self.assertEqual(user['password'], password)

    def test_get_users(self):
        url = self._get_url("users")
        r = requests.get(url)
        r_dict = json.loads(r.text)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r_dict[0]['description'], None)
        self.assertEqual(r_dict[0]['username'], self.user)

    def test_duplicate_user(self):
        payload = {'username': self.user, 'password': self.password}
        url = self._get_url("users")
        r = requests.post(url, json=payload)
        r_dict = json.loads(r.text)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r_dict['message'], "The username already exists")

    def test_show_user(self):
        url = self._get_url("users", self.user)
        headers = {'x-api-key': self.token}
        r = requests.get(url, headers=headers)
        r_dict = json.loads(r.text)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r_dict['ID'], 1)
        self.assertEqual(r_dict['name'], self.user)
        self.assertEqual(r_dict['password'], self.password)
        self.assertEqual(r_dict['is_admin'], False)

    def test_delete_user(self):
        username = "delete_user"
        password = "1234"
        self._create_test_user(username, password)
        token = self._get_auth_token(username, password)
        url = self._get_url("users", username)
        headers = {'x-api-key': token}
        r = requests.delete(url, headers=headers)
        self.assertEqual(r.status_code, 200)
