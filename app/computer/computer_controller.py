import logging
from typing import Dict

from app.computer import simple_computer as simple
from app import game_data_methods
from app.data.game import Game, Player
from app.util import Optional

logger = logging.getLogger(__name__)


def automate_turn(game: Game, algorithm: str = 'simple') -> Dict:
    opt_player: Optional[Player] = game.up_next()
    if opt_player.is_empty():
        logger.error(f'No player is up next. {game.player_up_next.get()}')
        return {}
    player: Player = opt_player.get()

    turn: Dict = {}
    if algorithm == 'simple':
        turn = simple.generate_turn(player, game_data_methods.get_opponents_names_in_play(game, player), game)
    else:
        logger.error(f'Unexpected algorithm type {algorithm}')

    # DEBUG
    validate_cards_left(game)

    return turn


# Debug Methods
def validate_cards_left(game: Game):
    card_count = 0
    for player in game.players.values():
        card_count += len(player.get_cards())

    sets_declared = 0
    for team in game.teams.values():
        sets_declared += team.sets_won
    expected_card_count = 48 - (sets_declared * 6)

    if card_count != expected_card_count:
        logger.error('Card Count Mismatch!')
