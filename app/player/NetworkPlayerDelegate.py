import abc

from app.game.data import Turn, Declaration


class NetworkPlayerDelegate(abc.ABC):

    @abc.abstractmethod
    async def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        pass

    @abc.abstractmethod
    async def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        pass
