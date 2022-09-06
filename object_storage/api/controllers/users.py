from flask import Flask, request
from object_storage.db import models
from object_storage import exceptions
from flask_json_schema import JsonSchema, JsonValidationError
from flask_expects_json import expects_json
from object_storage.api.schema import schema
from object_storage.api.controllers.login import token_required, user_exists
from object_storage.api.controllers.containers import delete_container
import json
from sqlalchemy import delete
from functools import wraps
import datetime
import secrets
from datetime import timedelta
from flask import Blueprint
import logging


users_api = Blueprint('users_api', __name__)
LOG = logging.getLogger("object_storage")


def listUsers():
    users = models.db.session.query(models.User).all()
    return list(users)


@users_api.route('/users', methods=['GET'])
def get_users():
    return [item.name for item in listUsers()]


@users_api.route('/users', methods=['POST'])
@expects_json(schema.users_schema)
def make_users():
    user = request.get_json()
    username = user['username']
    if user_exists(username):
        raise exceptions.Exists("The username already exists")
    user_db = models.User(
        name=user.get("username"),
        password=user.get("password"))
    user_db.save()
    LOG.info("Created a new user: %s", username)
    user_dict = user_db._to_dict()
    return user_dict


@users_api.route('/users/<name>', methods=['GET'])
@token_required
def show_user(name, auth_user):
    if name != auth_user:
        raise exceptions.Forbidden()
    user_data = user_exists(name)
    return [(user_data[0].ID, user_data[0].name, user_data[0].password,
             user_data[0].created_at, user_data[0].isAdmin)]


@users_api.route('/users/<name>', methods=['DELETE'])
@token_required
def delete_user(name, auth_user):
    if name != auth_user:
        raise exceptions.Forbidden()
    db_container = models.db.session.query(models.Container).filter_by(owner=auth_user)
    auth_container = list(db_container)
    for container in auth_container:
        delete_container(container.name)
    models.db.session.query(models.User).filter_by(name=name).delete()
    models.db.session.commit()
    LOG.info("Deleted the user %s and all of their containers and files", name)
    return ""
