import abc


class Backend(abc.ABC):
    @abc.abstractmethod
    def delete_object(self, obj):
        pass

    @abc.abstractmethod
    def store_object(self, obj, payload):
        pass

    @abc.abstractmethod
    def create_container(self, container):
        pass

    @abc.abstractmethod
    def delete_container(self, container):
        pass

    @abc.abstractmethod
    def read_object(self, obj, payload):
        pass
