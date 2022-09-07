import testtools
import threading
from werkzeug import serving
import uuid
import os
import requests
import json

from object_storage.cmd import api
from object_storage import conf


class BaseTestCase(testtools.TestCase):
    app = None
    port = None
    server = None
    db_file = None

    user = "test_user"
    password = "test_password"
    auth_token = None
    container_name = "test_container"
    object_name = "test_object"

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls._create_app()

        cls._create_test_user()
        cls._get_auth_token()
        cls._create_test_container()
        cls._create_test_object()

    @classmethod
    def tearDownClass(cls):
        # import pdb; pdb.set_trace()
        if cls.server:
            cls.server.server_close()
        if cls.db_file and os.path.exists(cls.db_file):
            os.unlink(cls.db_file)

    @classmethod
    def _create_app(cls):
        cfg = cls._get_default_config()
        conf.CONF = cfg
        cls.app = api.create_app()
        cls.server = serving.make_server(
            host='127.0.0.1',
            port=0,
            app=cls.app,
            threaded=True)
        cls.port = cls.server.socket.getsockname()[1]
        worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        worker.start()

    @classmethod
    def _get_default_config(cls):
        cls.db_file = "/tmp/object_storage_%s.db" % str(uuid.uuid4())
        cfg = {
            "db_url": "sqlite:///%s" % cls.db_file,
            "file": {
                "container_directory": "/tmp/object_storage"
            }
        }
        return cfg

    @classmethod
    def _get_base_url(cls):
        return "http://127.0.0.1:%s" % cls.port

    @classmethod
    def _get_url(cls, *args):
        return "/".join([cls._get_base_url()] + list(args))

    @classmethod
    def _create_test_user(cls, username=None, password=None):
        if not username:
            username = cls.user
        if not password:
            password = cls.password
        payload = {'username': username, 'password': password}
        url = cls._get_url("users")
        r = requests.post(url, json=payload)
        cls._check_response(r)
        r_dict = json.loads(r.text)
        return r_dict

    @classmethod
    def _get_auth_token(cls, username=None, password=None):
        if username and password:
            payload = {'username': username, 'password': password}
            url = cls._get_url("auth")
            r = requests.post(url, json=payload)
            r_dict = json.loads(r.text)
            token = r_dict['token']
            assert(r.status_code == 200)  
            return token
        if cls.auth_token:
            return cls.auth_token
        payload = {'username': cls.user, 'password': cls.password}
        url = cls._get_url("auth")
        r = requests.post(url, json=payload)
        r_dict = json.loads(r.text)
        cls.token = r_dict['token']
        assert(r.status_code == 200)  
        return cls.token

    @classmethod
    def _create_test_container(cls, name=None):
        if not name:
            name=cls.container_name
        payload = {'name': name}
        url = cls._get_url("containers")
        headers = {'x-api-key': cls.token}
        r = requests.post(url, headers=headers, json=payload)
        assert(r.status_code == 200)

    @classmethod
    def _create_test_object(cls, name=None):
        if not name:
            name=cls.object_name
        payload = {'name': name}
        url = cls._get_url("containers", cls.container_name)
        headers = {'x-api-key': cls.token}
        r = requests.post(url, headers=headers, json=payload)
        r_dict = json.loads(r.text)
        assert(r.status_code == 200)
        return r_dict

    @classmethod
    def _check_response(cls, response):
        if response.status_code >= 300:
            raise Exception(
                "Unexpected status code: %s. message: %s",
                response.status_code,
                response.text)
