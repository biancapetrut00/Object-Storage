from flask import Flask, request
from flask_expects_json import expects_json


app = Flask(__name__)


schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string',  "minLength": 4, "maxLength": 15},
        'password': {'type': 'string'}
    },
    'required': ['username', 'password']
}


@app.route('/', methods=['POST'])
@expects_json(schema)
def index():
    values = request.get_json()
    print(values)
    return values

if __name__ == '__main__':
        app.run(host='0.0.0.0')




# import datetime
# from datetime import timedelta
# datetime1 = datetime.datetime.now()
# delta = timedelta(minutes=10)
# datetime2 = datetime1 + delta
# print(datetime1)
# print(datetime2)
# if datetime1 < datetime2:
#     print("yes")