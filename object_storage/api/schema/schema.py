users_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string",  "minLength": 3, "maxLength": 32},
        "password": {"type": "string",  "minLength": 3, "maxLength": 64},
        "description": {"type": "string"}
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