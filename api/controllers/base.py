import os
import sys
sys.path.append('/home/bianca/workspace/Project')
print(sys.path)
from flask import Flask, render_template, request, jsonify
from object_storage.db import models 
from flask_json_schema import JsonSchema, JsonValidationError
from flask_expects_json import expects_json
from object_storage.api.schema import schema
import json
from sqlalchemy import delete
import secrets
import datetime
from datetime import timedelta

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

    @app.route('/')
    def index():
        return render_template('index.html')


    @app.route('/registeruser', methods=['POST'])
    @expects_json(schema.users_schema)
    def register():
        user = request.get_json()
        username = user['username']
        users = models.db.session.query(models.User).all()
        users_list = [x._to_dict() for x in users]
        for item in users_list:
            if item['name'] == username:
                return "user already exists"
        user_db = models.User(
            name=user.get("username"),
            password=user.get("password"))
        user_db.save()
        user_dict = user_db._to_dict()
        return user_dict

    @app.route('/users', methods=['GET'])
    def get_users():
        users = models.db.session.query(models.User).all()
        users_list = [x._to_dict() for x in users]
        # username_list = [item['name'] for item in user_list]
        # user_string = ""
        # for i in username_list:
        #     user_string = user_string + "username: " + str(i) + "\n"
        return [item['name'] for item in users_list]

    @app.route('/users/<name>', methods=['GET', 'DELETE'])
    def show_user(name):
        
        headers = request.headers
        auth = headers.get("X-Api-Key")

        datetime1 = datetime.datetime.now()
        delta = timedelta(minutes=10)
        datetime2 = datetime1 + delta
        tokens = models.db.session.query(models.AuthToken).all()
        tokens_list = [x._to_dict() for x in tokens]
        for item in tokens_list:
            if item['expireDate'] > datetime1 and item['token'] == auth:
                users = models.db.session.query(models.User).all()
                users_list = [x._to_dict() for x in users]
                containers = models.db.session.query(models.Container).all()
                containers_list = [x._to_dict() for x in containers]
                if request.method == 'GET':
                    return [(item['ID'], item['name'], item['password'], item['created_at'], 
                        item['isAdmin']) for item in users_list if item['name'] == name]
                elif request.method == 'DELETE':
                    models.db.session.query(models.User).filter_by(name=name).delete()
                    models.db.session.commit()
                    return "success"
        return "cannot access this page"

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
                delta = timedelta(minutes=10)
                datetime2 = datetime1 + delta
                tokens = models.db.session.query(models.AuthToken).all()
                tokens_list = [x._to_dict() for x in tokens]
                for item in tokens_list:
                    if item['expireDate'] > datetime1 and item['user'] == username:
                        return "already logged in"

                auth_db = models.AuthToken(
                token = token,
                user = username,
                expireDate = datetime2)
                auth_db.save()
                auth_dict = auth_db._to_dict()
                return auth_dict
        return "failed authentication"


    @app.route('/check')
    def check():
        headers = request.headers
        auth = headers.get("X-Api-Key")
        if auth == 'asoidewfoef':
            return "ok"
        return "failed"



    @app.route('/createcontainers', methods=['POST'])
    @expects_json(schema.container_schema)
    def create_containers():
        container = request.get_json()
        container_db = models.Container(
            name=container.get("name"), 
            description=container.get("description"),
            owner=container.get("owner"))
        container_db.save()
        container_dict = container_db._to_dict()
        return container_dict


    @app.route('/containers', methods=['GET'])
    def containers():
        headers = request.headers
        auth = headers.get("X-Api-Key")

        datetime1 = datetime.datetime.now()
        delta = timedelta(minutes=10)
        datetime2 = datetime1 + delta
        tokens = models.db.session.query(models.AuthToken).all()
        tokens_list = [x._to_dict() for x in tokens]
        for item in tokens_list:
            if item['expireDate'] > datetime1 and item['token'] == auth:
                name = item['user']
                containers = models.db.session.query(models.Container).all()
                containers_list = [x._to_dict() for x in containers]
                return [(c['name'], c['description']) for c in containers_list if c['owner'] == name]
        return "cannot access this page"




    @app.route('/createobject', methods=['POST'])
    @expects_json(schema.object_schema)
    def objects():
        objects = request.get_json()
        objects_db = models.Object(
            name=objects.get("name"),
            description=objects.get("description"),
            container=objects.get("container"))
        objects_db.save()
        objects_dict = objects_db._to_dict()
        return objects_dict



    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    return app
create_app()