from object_storage.backend import file


def get_backend():
    # for now, we only support the file backend
    return file.FileBackend()
