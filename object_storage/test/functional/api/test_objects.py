from object_storage.test.functional.api import base
from object_storage.db import models
from object_storage.backend import factory
import requests
import json
from flask import request
from types import SimpleNamespace

class ObjectTests(base.BaseTestCase):
    def test_create_object(self):
        name = "new_object"
        obj = self._create_test_object(name)
        self.assertEqual(obj['name'], name)
        self.assertEqual(obj['container'], self.container_name)
        self.assertEqual(obj['description'], None)

    def test_upload_object_data(self):
        payload = "test payload"
        url = self._get_url(
            "containers",
            self.container_name,
            self.object_name,
            "data")
        headers = {'x-api-key': self.token}
        #files = {'file': ('testfile.txt', 'some,data,to,send')}
        r = requests.put(url, headers=headers, data=payload)
        self.assertEqual(r.status_code, 200)

        url2 = self._get_url(
            "containers",
            self.container_name,
            self.object_name,
            "data")
        r2 = requests.get(url2, headers=headers)
        print(r2.text)
        self.assertEqual(r2.text, payload)

