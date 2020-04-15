import logging
from pandas import DataFrame

logger = logging.getLogger(__name__)


class Player:

    def __init__(self, name: str, player_type: str, team: str, cards: tuple, state: DataFrame):
        self.player_type: str = player_type
        self.name: str = name
        self.team: str = team
        self.cards: tuple = cards
        self.state: DataFrame = state

    def has_card(self, card: str) -> bool:
        return card in self.cards

    @property
    def in_play(self) -> bool:
        return len(self.cards) > 0
