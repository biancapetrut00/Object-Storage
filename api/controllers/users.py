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
import secrets
from datetime import timedelta
from flask import Blueprint
#from object_storage.api.controllers.base import token_required

users_api = Blueprint('users_api', __name__)


def user_exists(username):
    db_user = models.db.session.query(models.User).filter_by(name=username)
    auth_user = list(db_user)
    if len(auth_user) == 0:
        return 0
    return auth_user


def listUsers():
    users = models.db.session.query(models.User).all()
    return list(users)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        headers = request.headers
        if 'X-Api-Key' in headers:
            token = headers.get("X-Api-Key")
        else:
            raise exceptions.Unauthorized()
        datetime1 = datetime.datetime.now()
        db_token = models.db.session.query(models.AuthToken).filter_by(token=token)
        auth_token = list(db_token)
        if len(auth_token) == 0:
            raise exceptions.Unauthorized()
        if auth_token[0].expireDate <= datetime1:
            raise exceptions.Unauthorized()
        kwargs['auth_user'] = auth_token[0].user
        return f(*args, **kwargs)
    return decorator


@users_api.route('/auth', methods=['POST'])
@expects_json(schema.users_schema)
def auth():
    user = request.get_json()
    username = user['username']
    password = user['password']
    auth_user = user_exists(username)
    if auth_user == 0:
        raise exceptions.Unauthorized()
    if auth_user[0].password != password:
        raise exceptions.Unauthorized()
    token = secrets.token_hex(16)
    datetime1 = datetime.datetime.now()
    delta = timedelta(minutes=100)
    datetime2 = datetime1 + delta
    db_token = models.db.session.query(models.AuthToken).filter_by(user=username)
    auth_token = list(db_token)
    for item in auth_token:
        if item.expireDate > datetime1:
            raise exceptions.Conflict()
    auth_db = models.AuthToken(
    token = token,
    user = username,
    expireDate = datetime2)
    auth_db.save()
    auth_dict = auth_db._to_dict()
    return auth_dict


@users_api.route('/users', methods=['GET'])
def get_users():
    return [item.name for item in listUsers()]

@users_api.route('/users', methods=['POST'])
@expects_json(schema.users_schema)
def make_users():
    user = request.get_json()
    username = user['username']
    #for item in listUsers():
    if user_exists(username):
        raise exceptions.Exists()
    user_db = models.User(
        name=user.get("username"),
        password=user.get("password"))
    user_db.save()
    user_dict = user_db._to_dict()
    return user_dict


@users_api.route('/users/<name>', methods=['GET'])
@token_required
def show_user(name, auth_user):
    if name != auth_user:
        raise exceptions.Forbidden()
    user_data = user_exists(name)
    return [(user_data[0].ID, user_data[0].name, user_data[0].password, user_data[0].created_at, user_data[0].isAdmin)]


@users_api.route('/users/<name>', methods=['DELETE'])
@token_required
def delete_user(name, auth_user):
    if name != auth_user:
        raise exceptions.Forbidden()
    models.db.session.query(models.User).filter_by(name=name).delete()
    models.db.session.commit()
    return ""
