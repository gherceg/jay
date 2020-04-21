from typing import Dict, Set
from pandas import DataFrame

from app.data import Team, Player
from app.constants import *
from app.util import Optional


class Game:

    def __init__(self, pin: int, players: Dict[str, Player], teams: Dict[str, Team], state: DataFrame, up_next: Optional[str], options: Set[str]):
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
