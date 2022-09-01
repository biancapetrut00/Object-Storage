import os
import sys
sys.path.append('/home/bianca/workspace/Project')
print(sys.path)
from flask import Flask, render_template, request, jsonify, abort
from object_storage.db import models 
from object_storage.api.controllers import exceptions
from flask_json_schema import JsonSchema, JsonValidationError
from flask_expects_json import expects_json
from object_storage.api.schema import schema
import json
from sqlalchemy import delete
import secrets
import datetime
from datetime import timedelta
from functools import wraps

def create_app(test_config=None):
    app = Flask(__name__, template_folder='../../templates', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'object_storage.sqlite'),
    )
    models.register_app(app)


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


    def token_required(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            headers = request.headers
            if 'X-Api-Key' in headers:
                token = headers.get("X-Api-Key")
            else:
                raise exceptions.Unauthorized()
                #return "no token provided", 401
            datetime1 = datetime.datetime.now()
            db_token = models.db.session.query(models.AuthToken).filter_by(token=token)
            auth_token = [x._to_dict() for x in db_token]
            if len(auth_token) == 0:
                raise exceptions.Unauthorized()
                #return "authentication failure", 401
            if auth_token[0]['expireDate'] <= datetime1:
                raise exceptions.Unauthorized()
                #return "token expired", 401
            kwargs['auth_user'] = auth_token[0]['user']
            return f(*args, **kwargs)
        return decorator


    def user_exists(username):
        db_user = models.db.session.query(models.User).filter_by(name=username)
        auth_user = [x._to_dict() for x in db_user]
        if len(auth_user) == 0:
            return 0
        return auth_user

    def container_exists(container):
        db_container = models.db.session.query(models.Container).filter_by(name=container)
        auth_container = [x._to_dict() for x in db_container]
        if len(auth_container) == 0:
            return 0
        return auth_container

    def object_exists(object_name):
        db_object = models.db.session.query(models.Object).filter_by(name=object_name)
        auth_object = [x._to_dict() for x in db_object]
        if len(auth_object) == 0:
            return 0
        return auth_object


    @app.route('/auth', methods=['POST'])
    @expects_json(schema.users_schema)
    def auth():
        user = request.get_json()
        username = user['username']
        password = user['password']
        auth_user = user_exists(username)
        if auth_user == 0:
            raise exceptions.Unauthorized()
        if auth_user[0]["password"] != password:
            raise exceptions.Unauthorized()
        token = secrets.token_hex(16)
        datetime1 = datetime.datetime.now()
        delta = timedelta(minutes=100)
        datetime2 = datetime1 + delta
        db_token = models.db.session.query(models.AuthToken).filter_by(user=username)
        auth_token = [x._to_dict() for x in db_token]
        if len(auth_token) !=0:
            for item in auth_token:
                if item['expireDate'] > datetime1:
                    return "already logged in", 409
        auth_db = models.AuthToken(
        token = token,
        user = username,
        expireDate = datetime2)
        auth_db.save()
        auth_dict = auth_db._to_dict()
        return auth_dict


    def listUsers():
        users = models.db.session.query(models.User).all()
        return [x._to_dict() for x in users]


    @app.route('/users', methods=['GET'])
    def get_users():
        return [item['name'] for item in listUsers()]

    @app.route('/users', methods=['POST'])
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


    @app.route('/users/<name>', methods=['GET', 'DELETE'])
    @token_required
    def show_user(name, auth_user):
        if request.method == 'GET':
            user_data = user_exists(name)
            return [(user_data[0]['ID'], user_data[0]['name'], user_data[0]['password'], user_data[0]['created_at'], user_data[0]['isAdmin'])]
        elif request.method == 'DELETE':
            models.db.session.query(models.User).filter_by(name=name).delete()
            models.db.session.commit()
            return "success"


    @app.route('/containers', methods=['GET'])
    @token_required
    def get_containers(auth_user):
        db_container = models.db.session.query(models.Container).filter_by(owner=auth_user)
        auth_container = [x._to_dict() for x in db_container]
        if len(auth_container):
            return [(i['name'], i['description']) for i in auth_container]
        return "there are no containers for this user"

    @app.route('/containers', methods=['POST'])
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


    @app.route('/containers/<container>', methods=['GET', 'DELETE', 'HEAD'])
    @token_required
    def get_objects(container, auth_user):
        c_exists = container_exists(container)
        if c_exists == 0:
            raise exceptions.NotFound()
        for c in c_exists:
            if c['owner'] == auth_user:
                if request.method == 'GET':
                    db_object = models.db.session.query(models.Object).filter_by(container=container)
                    current_container_objects = [x._to_dict() for x in db_object]
                    return [(c['name'], c['description'], c['owner'])] + [(obj['name'], obj['description']) for obj in current_container_objects]
                elif request.method == 'HEAD':
                    return [(c['name'], c['description'], c['owner'])]
                elif request.method == 'DELETE':
                    models.db.session.query(models.Container).filter_by(name=container).delete()
                    models.db.session.commit()
                    return "success"


    @app.route('/containers/<container>', methods=['POST'])
    @expects_json(schema.object_schema)
    @token_required
    def make_objects(container, auth_user):
        c_exists = container_exists(container)
        if c_exists == 0:
            raise exceptions.NotFound()
        for c in c_exists:
            if c['owner'] == auth_user:
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


    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    return app
create_app()