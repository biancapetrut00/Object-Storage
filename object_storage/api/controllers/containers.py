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

containers_api = Blueprint('containers_api', __name__)


def container_exists(container):
    db_container = models.db.session.query(models.Container).filter_by(name=container)
    auth_container = list(db_container)
    if len(auth_container) == 0:
        return 0
    return auth_container


@containers_api.route('/containers', methods=['GET'])
@token_required
def get_containers(auth_user):
    db_container = models.db.session.query(models.Container).filter_by(owner=auth_user)
    auth_container = list(db_container)
    return [(i.name, i.description) for i in auth_container]


@containers_api.route('/containers', methods=['POST'])
@expects_json(schema.container_schema)
@token_required
def make_containers(auth_user):
    container = request.get_json()
    if container_exists(container['name']):
        raise exceptions.Exists()
    container_db = models.Container(
        name=container.get("name"),
        description=container.get("description"),
        owner=auth_user)
    container_db.save()
    container_dict = container_db._to_dict()
    return container_dict


@containers_api.route('/containers/<container>', methods=['GET', 'HEAD'])
@token_required
def get_objects(container, auth_user):
    c_exists = container_exists(container)
    if c_exists[0].owner != auth_user:
        raise exceptions.Forbidden()
    if c_exists == 0:
        raise exceptions.NotFound()
    for c in c_exists:
        if c.owner == auth_user:
            if request.method == 'GET':
                db_object = models.db.session.query(models.Object).filter_by(container=container)
                current_container_objects = list(db_object)
                return [(c.name, c.description,
                         c.owner)] + [(obj.name,
                                       obj.description) for obj in current_container_objects]
            elif request.method == 'HEAD':
                return [(c.name, c.description, c.owner)]


@containers_api.route('/containers/<container>', methods=['DELETE'])
@token_required
def delete_container(container, auth_user):
    c_exists = container_exists(container)
    if c_exists[0].owner != auth_user:
        raise exceptions.Forbidden()
    if c_exists == 0:
        raise exceptions.NotFound()
    for c in c_exists:
        if c.owner == auth_user:
            models.db.session.query(models.Container).filter_by(name=container).delete()
            models.db.session.commit()
            return ""
