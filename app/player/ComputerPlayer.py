import logging

from app.player import PlayerInterface, ComputerPlayerDelegate, state_methods
from app.game.data import Turn, Declaration, CardSet
from app.util import util_methods

logger = logging.getLogger(__name__)


class ComputerPlayer(PlayerInterface):
    delegate: ComputerPlayerDelegate = None

    def set_delegate(self, delegate: ComputerPlayerDelegate):
        self.delegate = delegate

    # PlayerInterface Methods
    async def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)
        if self.name == self.delegate.get_next_turn():
            await self.generate_turn()

    async def received_declaration(self, declaration: Declaration):
        super().received_declaration(declaration)
        if self.name == self.delegate.get_next_turn():
            await self.generate_turn()

    def eligible_sets(self) -> tuple:
        cards = self.get_cards()
        sets = set()
        for card in cards:
            sets.add(util_methods.set_for_card(card))

        return tuple(sets)

    async def generate_turn(self):
        logger.info(f'{self.name} is generating a turn')
        # first check if computer knows where all of the cards of a certain set are
        team_players = (self.name,) + self.teammates
        for card_set in CardSet:
            opt_declared_map = state_methods.able_to_declare(self.state, team_players, card_set)
            if opt_declared_map.is_present():
                logger.info(f'Declared map: {opt_declared_map.get()}')
                await self.delegate.computer_generated_declaration(self.name, card_set, opt_declared_map.get())
                return

        # could not declare, so ask a question
        sets = self.eligible_sets()
        card, player = state_methods.get_eligible_question_pair(self.state, sets, self.opposing_team)
        logger.info(f'Asking for the {card} from {player}')
        await self.delegate.computer_generated_turn(self.name, player, card)
