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
from object_storage.backend import factory


objects_api = Blueprint('objects_api', __name__)


def object_exists(object_name):
    db_object = models.db.session.query(models.Object).filter_by(name=object_name)
    auth_object = list(db_object)
    if len(auth_object) == 0:
        return 0
    return auth_object[0]


@objects_api.route('/containers/<container>', methods=['POST'])
@expects_json(schema.object_schema)
@token_required
def make_objects(container, auth_user):
    c_exists = container_exists(container)
    if c_exists == 0:
        raise exceptions.NotFound()
    if c_exists[0].owner != auth_user:
        raise exceptions.Forbidden()
    obj = request.get_json()
    if object_exists(obj['name']):
        raise exceptions.Exists()
    obj_db = models.Object(
        name=obj.get("name"),
        description=obj.get("description"),
        container=container)
    obj_db.save()
    obj_dict = obj_db._to_dict()

    return obj_dict

@objects_api.route('/containers/<container>/<obj>/data', methods=['PUT'])
@token_required
def upload_objects(container, obj, auth_user):
    c_exists = container_exists(container)
    if c_exists == 0:
        raise exceptions.NotFound()
    if c_exists[0].owner != auth_user:
        raise exceptions.Forbidden()
    obj_db = object_exists(obj)
    if not obj_db:
        raise exceptions.NotFound("object not found")

    backend = factory.get_backend()
    backend.store_object(obj_db, request.stream)
    return obj_db._to_dict()
