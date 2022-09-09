from flask import Flask, request
from object_storage import exceptions
from flask import Blueprint

status_api = Blueprint('status_api', __name__)

@status_api.route('/status')
@status_api.route('/')
def get_status():
    return ""

