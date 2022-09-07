import testtools
import threading
from werkzeug import serving
import uuid
import os

from object_storage.cmd import api
from object_storage import conf


class BaseTestCase(testtools.TestCase):
    app = None
    port = None
    server = None
    db_file = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls._create_app()

    @classmethod
    def tearDownClass(cls):
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
        print(cls.server.host)

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