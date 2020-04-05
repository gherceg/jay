import logging

from app.player.StateMethods import *

logger = logging.getLogger(__name__)


class PlayerInterface:

    def __init__(self, name: str, teammates: tuple, opposing_team: tuple):
        self.name: str = name
        self.state: DataFrame = StateMethods.create_default_state(players=(name,) + teammates + opposing_team)
        self.teammates: tuple = teammates
        self.opposing_team: tuple = opposing_team

    def received_next_turn(self, turn: Turn):
        self.state = StateMethods.update_state_with_turn(self.state, turn)

    def received_declaration(self, declaration: Declaration):
        self.state = StateMethods.update_state_with_declaration(self.state, declaration)

    def set_initial_cards(self, cards: tuple):
        logger.info('Setting initial cards for {0}: {1}'.format(self.name, cards))
        self.state = StateMethods.update_state_upon_receiving_cards(self.state, self.name, cards)

    def has_card(self, card: str) -> bool:
        return card in self.get_cards()

    def get_cards(self) -> tuple:
        return StateMethods.get_cards_for_player(self.state, self.name)
