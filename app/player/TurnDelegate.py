import abc

from app.game.data.Turn import Turn
from app.game.data.Declaration import Declaration


class TurnDelegate(abc.ABC):

    @abc.abstractmethod
    async def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        pass

    @abc.abstractmethod
    async def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        pass
