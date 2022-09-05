import os
import sys
#sys.path.append('/home/bianca/workspace/Project')
from flask import Flask, request, jsonify
from object_storage.db import models
from object_storage import exceptions
from flask_json_schema import JsonSchema, JsonValidationError
from flask_expects_json import expects_json
from object_storage.api.schema import schema
import json
from sqlalchemy import delete
import secrets
import datetime
from datetime import timedelta
from functools import wraps
from object_storage.api.controllers.users import users_api
from object_storage.api.controllers.containers import containers_api
from object_storage.api.controllers.objects import objects_api
from object_storage import conf
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("conf", help="config file location")

def get_db_url():
    url = conf.CONF.get("db_url")
    if not url:
        raise Exception("no db url specified")
    return url

def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=get_db_url()
    )
    models.setup(app, get_db_url())

    app.register_blueprint(users_api)
    app.register_blueprint(containers_api)
    app.register_blueprint(objects_api)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(exceptions.BaseException)
    def handle_login_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    return app


def main():
    args = parser.parse_args()
    if not args.conf:
        raise Exception("missing config file")
    conf.load_conf(args.conf)

    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
