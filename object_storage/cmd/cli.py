import argparse
import requests
import json
import os

DEFAULT_OBJECT_STORAGE_URL = "http://127.0.0.1:5000"

def get_base_url():
    url = os.environ.get("OBJECT_STORAGE_URL",
        DEFAULT_OBJECT_STORAGE_URL)
    return url

def get_url(*args):
    return "/".join([get_base_url()] + list(args))

def get_file_path(file_name):
    base_directory = "/tmp/object_storage_data"
    return os.path.join(base_directory, file_name)

def get_auth_token():
    path = get_file_path("auth")
    with open(path, "r") as f:
        message = f.read()
    token_dict = json.loads(message)
    return(token_dict)

parser = argparse.ArgumentParser()
parser.add_argument("path", help="choose the route")
parser.add_argument("request_type", help="get/post/delete")
parser.add_argument("--name", help="input username")
parser.add_argument("--password", help="input password")
args = parser.parse_args()

def show_users():
    url = get_url("users")
    r = requests.get(url)
    r_dict = json.loads(r.text)
    return r_dict

def create_users():
    if not args.name or not args.password:
        return "please provide a name and password"
    url = get_url("users")
    username = args.name
    password = args.password
    print(username, password)
    payload = {'username': username, 'password': password}
    r = requests.post(url, json=payload)
    r_dict = json.loads(r.text)
    return r_dict

def login():
    if not args.name or not args.password:
        return "please provide a name and password"
    username = args.name
    password = args.password
    payload = {'username': username, 'password': password}
    url = get_url("auth")
    r = requests.post(url, json=payload)
    r_dict = json.loads(r.text)
    if not 'token' in r_dict.keys():
        return r_dict
    token = r_dict['token']
    token_dict = {'user': username, 'token': token}
    path = get_file_path("auth")
    message = json.dumps(token_dict)
    with open(path, "w") as f:
        f.write(message)
    return "successfully logged in"

def show_user():
    token_dict = get_auth_token()
    token = token_dict['token']
    user = token_dict['user']
    print(token)
    url = get_url("users", user)
    headers = {'x-api-key': token}
    r = requests.get(url, headers=headers)
    r_dict = json.loads(r.text)
    return r_dict



if args.path == "users" and args.request_type == "show":
    print(show_users())

if args.path == "users" and args.request_type == "create":
    print(create_users())

if args.path == "log" and args.request_type == "in":
    print(login())

if args.path == "user" and args.request_type =="show":
    print(show_user())
