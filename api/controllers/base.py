import os
import sys
sys.path.append('/home/bianca/workspace/Project')
print(sys.path)
from flask import Flask, render_template, request, jsonify
from object_storage.db import models as db
from flask_json_schema import JsonSchema, JsonValidationError
from flask_expects_json import expects_json
from object_storage.api.schema import schema

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, template_folder='../../templates', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'object_storage.sqlite'),
    )
    db.register_app(app)


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    # schema = JsonSchema(app)

    # todo_schema = {
    #     "type": "object", 
    #     "properties": {
    #         "username": { "type": "string" },
    #         "password": { "type": "string" }
    #     },
    #     "required": ["username", "password"]
    # }

    # todos = []

    # @app.errorhandler(JsonValidationError)
    # def validation_error(e):
    #     return jsonify({ 'error': e.message, 'errors': [validation_error.message for validation_error  in e.errors]})

    # @app.route('/register', methods=['GET', 'POST'])
    # @schema.validate(todo_schema)
    # def create_message():
    #     if request.method == 'POST':
    #         todos.append( request.get_json() )
    #         return jsonify({ 'success': True, 'message': 'Created todo' })
    #         print(todos)
    #     return jsonify(todos)


    @app.route('/registeruser', methods=['POST'])
    @expects_json(schema.users_schema)
    def register():
        user = request.get_json()
        #value_list = list(values.values())
        #username = value_list[0]
        #password = value_list[1]
        #db.User.create(username, password)
        user_db = db.User(
            name=user.get("username"),
            password=user.get("password"))
        user_db.save()
        user_dict = user_db._to_dict()
        return user_dict


    @app.route('/createcontainers', methods=['POST'])
    @expects_json(schema.container_schema)
    def containers():
        container = request.get_json()
        #container_list = list(container_values.values())

        #if len(container_list) == 2:
            #db.Container.create(container_list[0], None, container_list[1])
        #else:
        #db.Container.create(container_list[0], container_list[1], container_list[2])
        container_db = db.Container(
            name=container.get("name"), 
            description=container.get("description"),
            owner=container.get("owner"))
        container_db.save()
        container_dict = container_db._to_dict()
        #db.Container.create(container_values['name'], container_values['description'], container_values('owner'))
        #description=container_values['description']
        return container_dict

    @app.route('/createobject', methods=['POST'])
    @expects_json(schema.object_schema)
    def objects():
        objects = request.get_json()
        objects_db = db.Object(
            name=objects.get("name"),
            description=objects.get("description"),
            container=objects.get("container"))
        objects_db.save()
        objects_dict = objects_db._to_dict()
        return objects_dict




    # @app.route('/register')
    # def register():
    #     return render_template('register_user.html')

    # @app.route('/register', methods=['POST'])
    # def register():
    #     user_name = request.form
    #     user_password = request.form
    #     db.User.create(user_name, user_password)
    #     return "created account"



    if __name__ == '__main__':
        #db.User.create("somename", "somepass")
        app.run(host='0.0.0.0')
    return app
create_app()