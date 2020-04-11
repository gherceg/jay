import logging
from pandas import DataFrame

from app.player import state_methods
from app.game.data import Turn, Declaration

logger = logging.getLogger(__name__)


class PlayerInterface:

    def __init__(self, name: str, teammates: tuple, opposing_team: tuple, player_type: str):
        self.player_type = player_type
        self.name: str = name
        self.state: DataFrame = state_methods.create_default_state(players=(name,) + teammates + opposing_team)
        self.teammates: tuple = teammates
        self.opposing_team: tuple = opposing_team

        # TODO ideally pass this in but teams are horrendous right now and need to be refactored
        self.team_name = None

    def received_next_turn(self, turn: Turn, players_out_of_play: tuple):
        self.state = state_methods.update_state_with_turn(self.state, turn)
        self.state = state_methods.update_state_with_players_out_of_cards(self.state, players_out_of_play)
        self.state = state_methods.check_for_process_of_elimination(self.state)

    def received_declaration(self, declaration: Declaration, players_out_of_play: tuple):
        self.state = state_methods.update_state_with_declaration(self.state, declaration)
        self.state = state_methods.update_state_with_players_out_of_cards(self.state, players_out_of_play)
        self.state = state_methods.check_for_process_of_elimination(self.state)

    def set_initial_cards(self, cards: tuple):
        logger.info('Setting initial cards for {0}: {1}'.format(self.name, cards))
        self.state = state_methods.update_state_upon_receiving_cards(self.state, self.name, cards)

    def has_card(self, card: str) -> bool:
        return card in self.get_cards()

    @property
    def in_play(self) -> bool:
        return len(self.get_cards()) > 0

    def get_cards(self) -> tuple:
        return state_methods.get_cards_for_player(self.state, self.name)
