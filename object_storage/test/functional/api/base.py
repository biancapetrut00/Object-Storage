import testtools
import threading
from werkzeug import serving

from object_storage.cmd import api
from object_storage import conf


class BaseTestCase(testtools.TestCase):
    app = None
    port = None
    server = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls._create_app()

    @classmethod
    def tearDownClass(cls):
        if cls.server:
            cls.server.server_close()

    @classmethod
    def _create_app(cls):
        cfg = BaseTestCase._get_default_config()
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

    @staticmethod
    def _get_default_config():
        cfg = {
            "db_url": "sqlite:////tmp/object_storage.db",
            "file": {
                "container_directory": "/tmp/object_storage"
            }
        }
        return cfg


