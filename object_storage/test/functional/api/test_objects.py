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
        url = self._get_url("containers", self.container_name)
        headers = {'x-api-key': self.token}
        files = {'file': ('testfile.txt', 'some,data,to,send')}
        r = requests.put(url, headers=headers, files=files)
        obj_db = {
            "name": self.object_name,
            "container": self.container_name
        }
        n = SimpleNamespace(**obj_db)
        # obj_db = {}
        # obj_db.container = self.container_name
        # obj_db.name = self.object_name
        print(obj_db)
        backend = factory.get_backend()
        response = backend.read_object(n)
        self.assertEqual(response, 'some,data,to,send')
