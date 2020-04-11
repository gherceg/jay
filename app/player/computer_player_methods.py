import logging
import random
from pandas import DataFrame

from app.player import PlayerInterface, state_methods
from app.game.data import Turn, Declaration, CardSet, CardStatus
from app.util import util_methods
from app.constants import *

logger = logging.getLogger(__name__)


def generate_turn(player: PlayerInterface, eligible_player_names: tuple) -> dict:
    # team_players = (player.name,) + player.teammates
    # set_to_declare = None
    # highest_score = -1
    # for card_set in CardSet:
    #     score_for_set = score_declaration_for_set(player.state, team_players, card_set)
    #     if score_for_set > highest_score:
    #         highest_score = score_for_set
    #         set_to_declare = card_set
    # logger.info(f'Checking declaration: would declare {set_to_declare} with a score of {highest_score}')

    if len(eligible_player_names) == 0:
        # have to declare
        return attempt_to_declare(player)

    # first check if computer knows where all of the cards of a certain set are
    team_players = (player.name,) + player.teammates
    for card_set in CardSet:
        opt_declared_map = state_methods.able_to_declare(player.state, team_players, card_set)
        if opt_declared_map.is_present():
            return declaration_dict(player.name, card_set, opt_declared_map.get())

    # could not declare, so ask a question
    eligible_cards = util_methods.eligible_cards(player.get_cards())
    card, player_to_ask = get_eligible_question_pair(player.state, eligible_cards, eligible_player_names)
    if card is not None and player_to_ask is not None:
        return question_dict(player.name, player_to_ask, card)
    else:
        return attempt_to_declare(player)


def attempt_to_declare(player: PlayerInterface) -> dict:
    team_players = (player.name,) + player.teammates
    set_to_declare = None
    highest_score = -1
    for card_set in CardSet:
        score_for_set = score_declaration_for_set(player.state, team_players, card_set)
        if score_for_set > highest_score:
            highest_score = score_for_set
            set_to_declare = card_set

    declared_map = []
    for card in set_to_declare.value:
        team_rows = player.state.loc[card, list(team_players)]
        player_for_card = None
        team_has_card = team_rows[team_rows == CardStatus.DOES_HAVE]
        if len(team_has_card) == 0:
            team_might_have_card = team_rows[team_rows == CardStatus.MIGHT_HAVE]
            if len(team_might_have_card) == 0:
                team_unknown = team_rows[team_rows == CardStatus.UNKNOWN]
                if len(team_unknown) == 0:
                    team_does_not_have = team_rows[team_rows == CardStatus.DOES_NOT_HAVE]
                    logger.error(
                        f'Computer is being forced to declare even though it is not possible. Should not happen.\n\{player.get_card()}n{player.state}')
                    player_for_card = team_does_not_have.keys()[0]
                else:
                    player_for_card = team_unknown.keys()[0]
            else:
                player_for_card = team_might_have_card.keys()[0]
        else:
            player_for_card = team_has_card.keys()[0]

        pair = {CARD: card, PLAYER: player_for_card}
        declared_map.append(pair)

    return declaration_dict(player.name, set_to_declare, tuple(declared_map))


def score_declaration_for_set(state: DataFrame, team: tuple, card_set: CardSet) -> int:
    accumulated_score = 1
    for card in card_set.value:
        team_rows = state.loc[card, list(team)]
        team_has_card = team_rows[team_rows == CardStatus.DOES_HAVE]
        if len(team_has_card) == 0:
            team_might_have_card = team_rows[team_rows == CardStatus.MIGHT_HAVE]
            if len(team_might_have_card) == 0:
                team_unknown = team_rows[team_rows == CardStatus.UNKNOWN]
                if len(team_unknown) == 0:
                    accumulated_score *= 0
                else:
                    accumulated_score *= 1
            else:
                accumulated_score *= 2
        else:
            accumulated_score *= 3

    return accumulated_score


def get_eligible_question_pair(state: DataFrame, cards_to_ask_for: tuple, opponents: tuple) -> (str, str):
    opponents_df = state.loc[list(cards_to_ask_for), list(opponents)]

    have_df = opponents_df[opponents_df[list(opponents)] == CardStatus.DOES_HAVE]
    have = list(have_df[have_df.notnull()].stack().index)

    might_have_df = opponents_df[opponents_df[list(opponents)] == CardStatus.MIGHT_HAVE]
    might_have = list(might_have_df[might_have_df.notnull()].stack().index)

    unknown_df = opponents_df[opponents_df[list(opponents)] == CardStatus.UNKNOWN]
    unknown = list(unknown_df[unknown_df.notnull()].stack().index)

    does_not_have_df = opponents_df[opponents_df[list(opponents)] == CardStatus.DOES_NOT_HAVE]
    does_not_have = list(does_not_have_df[does_not_have_df.notnull()].stack().index)

    total_card_count = opponents_df.size
    percent_does_have = (len(have) / total_card_count) * 100
    percent_might_have = (len(might_have) / total_card_count) * 100
    percent_unknown = (len(unknown) / total_card_count) * 100
    percent_does_not_have = (len(does_not_have) / total_card_count) * 100
    logger.debug(
        'Computer Turn - Does Have: {:.0f}%, Might Have: {:.0f}%, Unknown: {:.0f}%, Does Not Have: {:.0f}%'
            .format(percent_does_have, percent_might_have, percent_unknown, percent_does_not_have))
    if len(have) > 0:
        return random.choice(have)
    elif len(might_have) > 0:
        return random.choice(might_have)
    elif len(unknown) > 0:
        return random.choice(unknown)
    elif len(does_not_have) > 0:
        return None, None
    else:
        logger.info(state)
        raise Exception('No options left')


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
