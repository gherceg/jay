import logging
from pandas import DataFrame
# ideally would not need this and just set cards on the player
from app.game_state import get_cards_for_player

logger = logging.getLogger(__name__)


class Player:

    def __init__(self, name: str, player_type: str, team_name: str, teammates: tuple, opponents: tuple, state: DataFrame):
        self.player_type: str = player_type
        self.name: str = name
        self.team_name: str = team_name
        self.teammates = teammates
        self.opponents = opponents
        self.state: DataFrame = state

    def has_card(self, card: str) -> bool:
        return card in self.get_cards()

    @property
    def in_play(self) -> bool:
        return len(self.get_cards()) > 0

    def get_cards(self) -> tuple:
        return get_cards_for_player(self.state, self.name)
