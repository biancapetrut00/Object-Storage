from flask import Flask, request
from object_storage.db import models
from object_storage import exceptions
from flask_json_schema import JsonSchema, JsonValidationError
from flask_expects_json import expects_json
from object_storage.api.schema import schema
import json
from sqlalchemy import delete
from functools import wraps
import datetime
from datetime import timedelta
from flask import Blueprint
from object_storage.api.controllers.users import token_required
from object_storage.api.controllers.containers import container_exists


objects_api = Blueprint('objects_api', __name__)


def object_exists(object_name):
    db_object = models.db.session.query(models.Object).filter_by(name=object_name)
    auth_object = list(db_object)
    if len(auth_object) == 0:
        return 0
    return auth_object


@objects_api.route('/containers/<container>', methods=['POST'])
@expects_json(schema.object_schema)
@token_required
def make_objects(container, auth_user):
    c_exists = container_exists(container)
    if c_exists[0].owner != auth_user:
        raise exceptions.Forbidden()
    if c_exists == 0:
        raise exceptions.NotFound()
    for c in c_exists:
        if c.owner == auth_user:
            objects = request.get_json()
            if object_exists(objects['name']):
                raise exceptions.Exists()
            objects_db = models.Object(
                name=objects.get("name"),
                description=objects.get("description"),
                container=container)
            objects_db.save()
            objects_dict = objects_db._to_dict()
            return objects_dict
