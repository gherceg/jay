import logging

from app.player import PlayerInterface, ComputerPlayerDelegate, state_methods
from app.game.data import Turn, Declaration, CardSet
from app.util import util_methods

logger = logging.getLogger(__name__)


class ComputerPlayer(PlayerInterface):
    delegate: ComputerPlayerDelegate = None

    def set_question_delegate(self, delegate: ComputerPlayerDelegate):
        self.delegate = delegate

    def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)
        if self.name == self.delegate.get_next_turn():
            self.generate_turn()

    def received_declaration(self, declaration: Declaration):
        super().received_declaration(declaration)

    def eligible_sets(self) -> tuple:
        cards = self.get_cards()
        sets = set()
        for card in cards:
            sets.add(util_methods.set_for_card(card))

        return tuple(sets)


    def generate_turn(self):
        # first check if computer knows where all of the cards of a certain set are
        team_players = (self.name,) + self.teammates
        for card_set in CardSet:
            opt_declared_map = state_methods.able_to_declare(self.state, team_players, card_set)
            if opt_declared_map.is_present():
                logger.info(f'Declared map: {opt_declared_map.get()}')
                self.delegate.computer_generated_declaration(self.name, card_set, opt_declared_map.get())
                return

        # could not declare, so ask a question
        sets = self.eligible_sets()
        # state_methods.get_eligible_question_pair

