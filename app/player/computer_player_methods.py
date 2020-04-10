import logging
from pandas import DataFrame

from app.player import PlayerInterface, state_methods
from app.game.data import Turn, Declaration, CardSet
from app.util import util_methods
from app.constants import *

logger = logging.getLogger(__name__)





def generate_turn(player: PlayerInterface) -> dict:
    # first check if computer knows where all of the cards of a certain set are
    team_players = (player.name,) + player.teammates
    for card_set in CardSet:
        opt_declared_map = state_methods.able_to_declare(player.state, team_players, card_set)
        if opt_declared_map.is_present():
            logger.info(f'Declared map: {opt_declared_map.get()}')
            return declaration_dict(player.name, card_set, opt_declared_map.get())

    # could not declare, so ask a question
    sets = util_methods.eligible_sets(player.get_cards())
    card, player_to_ask = state_methods.get_eligible_question_pair(player.state, sets, player.opposing_team)
    logger.info(f'{player.name} is asking {player_to_ask} for the {card}')
    return question_dict(player.name, player_to_ask, card)


def declaration_dict(name: str, card_set: CardSet, declared_map: tuple) -> dict:
    return {
        TURN_TYPE: DECLARATION,
        NAME: name,
        CARD_SET: card_set,
        DECLARED_MAP: declared_map
    }


def question_dict(questioner: str, respondent: str, card: str) -> dict:
    return {
        TURN_TYPE: QUESTION,
        QUESTIONER: questioner,
        RESPONDENT: respondent,
        CARD: card
    }
