users_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string",  "minLength": 4, "maxLength": 15},
        "password": {"type": "string"}
    },
    "required": ["username", "password"]
}

container_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'owner': {'type': 'string'}
    },
    'required': ['name', 'owner']
}

object_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'container': {'type': 'string'}
    },
    'required': ['name', 'container']
}