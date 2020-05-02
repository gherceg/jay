from typing import Dict, Set, List
from pandas import DataFrame

from app.constants import *
from app.util import Optional
# ideally would not need this and just set cards on the player
from app.game_state_updates import get_cards_for_player


class Player:

    def __init__(self, name: str, player_type: str, team_name: str, teammates: tuple, opponents: tuple,
                 state: DataFrame):
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

    def get_cards(self) -> List[str]:
        return get_cards_for_player(self.state, self.name)


class Team:

    def __init__(self, name: str, player_names: tuple, sets_won: int):
        self.name = name
        self.player_names = player_names
        self.sets_won = sets_won

    def to_dict(self) -> dict:
        return {
            NAME: self.name,
            PLAYERS: self.player_names,
            SET_COUNT: self.sets_won
        }


class Game:

    def __init__(self, pin: int, players: Dict[str, Player], teams: Dict[str, Team], state: DataFrame,
                 up_next: Optional[str], options: Set[str]):
        self.pin = pin
        self.players = players
        self.teams = teams
        self.ledger = []
        self.state = state
        self.options = options
        self.player_up_next: Optional[str] = up_next

    @property
    def virtual_deck(self) -> bool:
        return VIRTUAL_DECK in self.options
