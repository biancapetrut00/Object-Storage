import abc


class Backend(abc.ABC):
    @abc.abstractmethod
    def delete_object(obj):
        pass

    @abc.abstractmethod
    def create_object(obj):
        pass

    @abc.abstractmethod
    def store_object(obj, payload):
        pass

    @abc.abstractmethod
    def create_container(container):
        pass

    @abc.abstractmethod
    def delete_container(container):
        pass
