import logging

from app.constants import *

logger = logging.getLogger(__name__)


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