users_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string",  "minLength": 3, "maxLength": 15},
        "password": {"type": "string",  "minLength": 3, "maxLength": 15}
    },
    "required": ["username", "password"]
}

container_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'}
    },
    'required': ['name']
}

object_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'}
    },
    'required': ['name']
}