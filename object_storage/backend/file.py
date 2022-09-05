import os
from object_storage.backend import base
from flask import Blueprint, Flask, flash, request, send_from_directory, redirect, url_for
import hashlib
from object_storage import conf
import six


class FileBackend(base.Backend):
    def _hash_name(self, name):
        return hashlib.sha256(six.b(name)).hexdigest()

    def _get_base_container_directory(self):
        directory = conf.CONF.get('file', {}).get('container_directory')
        if not directory:
            raise exceptions.InvalidConfig("missing file backend directory")
        return directory

    def _get_container_path(self, container_name):
        base_directory = self._get_base_container_directory()
        if not container_name:
            raise exceptions.InvalidRequest("missing container name")
        return os.path.join(
            base_directory,
            self._hash_name(container_name))

    def _get_file_path(self, container_name, object_name):
        base_directory = self._get_base_container_directory()
        if not container_name:
            raise exceptions.InvalidRequest("missing container name")
        if not object_name:
            raise exceptions.InvalidRequest("missing object name")
        return os.path.join(
            base_directory,
            self._hash_name(container_name),
            self._hash_name(object_name))

    def delete_object(self, obj):
        raise NotImplemented()

    def store_object(self, obj, payload):
        if not obj.container:
            raise exceptions.InvalidRequest("no container specified")
        file_path = self._get_file_path(obj.container, obj.name)

        with open(file_path, "wb") as f:
            while True:
                chunk = payload.read(65 * 1024)
                if not chunk:
                    break
                f.write(chunk)



    def create_container(self, container):
        container_path = self._get_container_path(container.name)
        if not os.path.exists(container_path):
            os.makedirs(container_path)
        

    def delete_container(self, container):
        raise NotImplemented()


