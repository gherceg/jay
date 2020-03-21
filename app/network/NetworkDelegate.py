import abc

class NetworkDelegate(abc.ABC):

    @abc.abstractmethod
    def broadcast_message(self, client_id: str, contents: dict):
        pass
