import abc
from typing import Dict


class NetworkDelegate(abc.ABC):

    @abc.abstractmethod
    async def broadcast_message(self, client_id: str, contents: Dict):
        pass
