import abc

from app.game.data.Turn import Turn


class TurnDelegate(abc.ABC):

    @abc.abstractmethod
    def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        pass
