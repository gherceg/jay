import logging

from app.constants import *
from app.game import Game
from app.player import PlayerInterface
from app.util import Optional, util_methods

logger = logging.getLogger(__name__)


def validate_question(game: Game, data: dict) -> Optional[str]:
    # ensure the necessary keys are in data
    if QUESTIONER not in data or RESPONDENT not in data or CARD not in data:
        return Optional(f'Error processing question message: Missing keys.')

    questioner = data[QUESTIONER]
    respondent = data[RESPONDENT]
    card = data[CARD]
    valid_cards = util_methods.deck_of_cards()

    if questioner not in game.players or respondent not in game.players or card not in valid_cards:
        return Optional(f'Error processing question message: Unknown values for either players or cards.')

    player_asking: PlayerInterface = game.players[questioner]
    player_responding: PlayerInterface = game.players[respondent]

    # ensure players are on opposing teams
    if player_responding.name not in player_asking.opposing_team or player_asking.name not in player_responding.opposing_team:
        return Optional(f'Illegal Question: Players are not on opposing team')

    # ensure player asking question has other cards in that set
    cards_for_player = player_asking.get_cards()
    eligible_sets = util_methods.eligible_sets(cards_for_player)
    eligible_card = False
    for card_set in eligible_sets:
        if card in card_set.value:
            eligible_card = True
            break

    # ensure player can ask for card
    if not eligible_card or card in cards_for_player:
        return Optional(f'Illegal Question: {player_asking.name} cannot ask for the {card}')

    # ensure player being asked has cards left
    if len(player_responding.get_cards()) == 0:
        return Optional(f'Illegal Question: {player_responding.name} is out of cards.')

    return Optional.empty()
