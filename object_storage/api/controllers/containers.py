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
from object_storage.api.controllers.login import token_required
from object_storage.backend import factory
from object_storage.api.controllers.objects import delete_object, container_exists
import logging


containers_api = Blueprint('containers_api', __name__)
LOG = logging.getLogger("object_storage")


@containers_api.route('/containers', methods=['GET'])
@token_required
def get_container(auth_user):
    db_container = models.db.session.query(models.Container).filter_by(owner=auth_user)
    auth_container = list(db_container)
    return [(i.name, i.description) for i in auth_container]


@containers_api.route('/containers', methods=['POST'])
@expects_json(schema.container_schema)
@token_required
def make_containers(auth_user):
    container = request.get_json()
    if container_exists(container['name']):
        raise exceptions.Exists("The container already exists")
    container_db = models.Container(
        name=container.get("name"),
        description=container.get("description"),
        owner=auth_user)
    container_db.save()
    backend = factory.get_backend()
    backend.create_container(container_db)
    LOG.info("Created container: %s", container_db.name)
    container_dict = container_db._to_dict()
    return container_dict


@containers_api.route('/containers/<container>', methods=['GET', 'HEAD'])
@token_required
def get_objects(container, auth_user):
    c_exists = container_exists(container)
    if c_exists == 0:
        raise exceptions.NotFound("Container not found")
    if c_exists.owner != auth_user:
        raise exceptions.Forbidden()
    if request.method == 'GET':
        db_object = models.db.session.query(models.Object).filter_by(container=container)
        current_container_objects = list(db_object)
        return [(
            c_exists.name,
            c_exists.description,
            c_exists.owner)] + [(
                            obj.name,
                            obj.description)
            for obj in current_container_objects]
    elif request.method == 'HEAD':
        return [(c_exists.name, c_exists.description, c_exists.owner)]


@containers_api.route('/containers/<container>', methods=['DELETE'])
@token_required
def delete_container(container, auth_user):
    c_exists = container_exists(container)
    if c_exists == 0:
        raise exceptions.NotFound("Container not found")
    if c_exists.owner != auth_user:
        raise exceptions.Forbidden()
    db_object = models.db.session.query(models.Object).filter_by(container=container)
    current_container_objects = list(db_object)
    item_list = []
    for obj in current_container_objects:
        item_list.append(obj.name)
        delete_object(container, obj.name)
    items = ', '.join([str(elem) for elem in item_list])
    backend = factory.get_backend()
    backend.delete_container(c_exists)
    models.db.session.query(models.Container).filter_by(name=container).delete()
    models.db.session.commit()
    LOG.info("Deleted the " + c_exists.name +" container and all of the files inside: " + items)
    return ""
