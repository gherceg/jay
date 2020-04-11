import abc
from typing import Dict


class NetworkDelegate(abc.ABC):

    @abc.abstractmethod
    async def broadcast_message(self, name: str, contents: Dict):
        pass
