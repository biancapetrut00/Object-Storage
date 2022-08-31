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


    def token_required(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            if 'x-access-token' in request.headers:
                token = headers.get("X-Api-Key")
            else:
                return "no token provided", 1
            datetime1 = datetime.datetime.now()
            tokens = models.db.session.query(models.AuthToken).all()
            tokens_list = [x._to_dict() for x in tokens]
            for item in tokens_list:
                if item['expireDate'] > datetime1 and item['token'] == token:
                    return f(current_user, *args, **kwargs)
        return decorator




    @app.errorhandler(exceptions.BaseException)
    def handle_login_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


    @app.route('/auth', methods=['POST'])
    @expects_json(schema.users_schema)
    def auth():
        user = request.get_json()
        username = user['username']
        password = user['password']
        users = models.db.session.query(models.User).all()
        users_list = [x._to_dict() for x in users]
        for item in users_list:
            if item['name'] == username and item['password'] == password:
                token = secrets.token_hex(16)
                datetime1 = datetime.datetime.now()
                delta = timedelta(minutes=100)
                datetime2 = datetime1 + delta
                tokens = models.db.session.query(models.AuthToken).all()
                tokens_list = [x._to_dict() for x in tokens]
                for item in tokens_list:
                    if item['expireDate'] > datetime1 and item['user'] == username:
                        return "already logged in", 409
                auth_db = models.AuthToken(
                token = token,
                user = username,
                expireDate = datetime2)
                auth_db.save()
                auth_dict = auth_db._to_dict()
                return auth_dict
        #return "failed authentication", 401
        #import pdb; pdb.set_trace()
        raise exceptions.Unauthorized()
        #raise HTTPError(400, message='Something is wrong...')


    def login(auth_token):
        datetime1 = datetime.datetime.now()
        tokens = models.db.session.query(models.AuthToken).all()
        tokens_list = [x._to_dict() for x in tokens]
        for item in tokens_list:
            if item['expireDate'] > datetime1 and item['token'] == auth_token:
                return item['user']
        return 0


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
        for item in listUsers():
            if item['name'] == username:
                return "username already exists", 409
        user_db = models.User(
            name=user.get("username"),
            password=user.get("password"))
        user_db.save()
        user_dict = user_db._to_dict()
        return user_dict



    @app.route('/users/<name>', methods=['GET', 'DELETE'])
    @token_required
    def show_user(name):
        # headers = request.headers
        # auth = headers.get("X-Api-Key")
        # if login(auth):
        if request.method == 'GET':
            return [(item['ID'], item['name'], item['password'], item['created_at'], 
                item['isAdmin']) for item in listUsers() if item['name'] == name]
        elif request.method == 'DELETE':
            models.db.session.query(models.User).filter_by(name=name).delete()
            models.db.session.commit()
            return "success"
        raise exceptions.Forbidden()


    def listContainers():
        containers = models.db.session.query(models.Container).all()
        return [x._to_dict() for x in containers]


    @app.route('/containers', methods=['GET'])
    def get_containers():
        headers = request.headers
        auth = headers.get("X-Api-Key")
        login_name = login(auth)
        if login_name:
            return [(c['name'], c['description']) for c in listContainers() if c['owner'] == login_name]
        raise exceptions.Unauthorized()

    @app.route('/containers', methods=['POST'])
    @expects_json(schema.container_schema)
    def make_containers():
        headers = request.headers
        auth = headers.get("X-Api-Key")
        if login(auth):
            name = login(auth)
            container = request.get_json()
            for c in listContainers():
                if c['name'] == container['name']:
                    return "container already exists", 409
            container_db = models.Container(
            name=container.get("name"), 
            description=container.get("description"),
            owner=name)
            container_db.save()
            container_dict = container_db._to_dict()
            return container_dict
        raise exceptions.Unauthorized()


    def listObjects():
        objects = models.db.session.query(models.Object).all()
        return [x._to_dict() for x in objects]        


    @app.route('/containers/<container>', methods=['GET', 'DELETE', 'HEAD'])
    def get_objects(container):
        headers = request.headers
        auth = headers.get("X-Api-Key")
        if login(auth):
            name = login(auth)
            for c in listContainers():
                if c['owner'] == name and c['name'] == container:
                    if request.method == 'GET':
                        return [(c['name'], c['description'], c['owner'])] + [(obj['name'], obj['description']) for obj in listObjects()]
                    elif request.method == 'HEAD':
                        return [(c['name'], c['description'], c['owner'])]
                    elif request.method == 'DELETE':
                        models.db.session.query(models.Container).filter_by(name=container).delete()
                        models.db.session.commit()
                        return "success"
        raise exceptions.Unauthorized()


    @app.route('/containers/<container>', methods=['POST'])
    @expects_json(schema.object_schema)
    def make_objects(container):
        headers = request.headers
        auth = headers.get("X-Api-Key")
        if login(auth):
            name = login(auth)
            for c in listContainers():
                if c['owner'] == name and c['name'] == container:
                    objects = request.get_json()
                    for item in listObjects():
                        if item['name'] == objects['name']:
                            return "object already exists", 409
                    objects_db = models.Object(
                        name=objects.get("name"),
                        description=objects.get("description"),
                        container=container)
                    objects_db.save()
                    objects_dict = objects_db._to_dict()
                    return objects_dict
        raise exceptions.Unauthorized()



    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    return app
create_app()