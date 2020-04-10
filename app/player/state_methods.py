import logging
from pandas import DataFrame
import random

from app.game.data import Turn, Declaration, CardStatus, CardSet
from app.util import util_methods, data_frame_methods, Optional
from app.constants import *

logger = logging.getLogger(__name__)


def create_default_state(players: tuple) -> DataFrame:
    """Creates and returns a DataFrame object that contains a column for each player and a row for each card
        Each cell is set to the CardStatus UNKNOWN
    """
    cards = util_methods.deck_of_cards()
    return data_frame_methods.create_state_with_value(cards, players, CardStatus.UNKNOWN)


def update_state_upon_receiving_cards(state: DataFrame, player: str, cards: tuple):
    """Update column for player to DOES_HAVE for all cards specified, and DOES_NOT_HAVE for remaining rows"""

    # start by setting player's entire column to does not have
    state.loc[:, player] = CardStatus.DOES_NOT_HAVE

    # for the cards specified, set every player to does not have as well
    for card in cards:
        # error check - ensure that no other player already lists having this card
        if any(state.loc[card, :] == CardStatus.DOES_HAVE):
            # return error - INVALID CARD STATE
            raise Exception('Invalid Card Entry. A Card was already assigned to another player.')
        else:
            state.loc[card, :] = CardStatus.DOES_NOT_HAVE

    # finally, update specified cards to does have for player specified
    for card in cards:
        state.loc[card, player] = CardStatus.DOES_HAVE

    return state


def update_state_with_turn(state: DataFrame, turn: Turn) -> DataFrame:
    card_set: CardSet = util_methods.set_for_card(turn.card)

    if turn.outcome:
        # the questioner has the card so the rest do not
        state.loc[turn.card, :] = CardStatus.DOES_NOT_HAVE
        state.loc[turn.card, turn.questioner] = CardStatus.DOES_HAVE
    else:
        # both players do not have the given card
        state.loc[turn.card, turn.questioner] = CardStatus.DOES_NOT_HAVE
        state.loc[turn.card, turn.respondent] = CardStatus.DOES_NOT_HAVE

    # update any unknown statuses to might have for the player asking the question
    state = data_frame_methods.update_rows_with_old_to_new_for_column(state,
                                                                      card_set.value,
                                                                      turn.questioner,
                                                                      CardStatus.UNKNOWN,
                                                                      CardStatus.MIGHT_HAVE)
    return state


def update_state_with_declaration(state: DataFrame, declaration: Declaration) -> DataFrame:
    for player_card_pair in declaration.declared_map:
        state.loc[player_card_pair[CARD], :] = CardStatus.DECLARED

    return state


# Read Methods
def get_cards_for_player(state: DataFrame, player: str) -> tuple:
    card_rows = state.loc[:, player]
    cards = card_rows[card_rows == CardStatus.DOES_HAVE]
    return tuple(cards.keys())


def able_to_declare(state: DataFrame, team: tuple, card_set: CardSet) -> Optional[tuple]:
    declared_map = []
    for card in card_set.value:
        team_rows = state.loc[card, list(team)]
        team_has_card = team_rows[team_rows == CardStatus.DOES_HAVE]
        assert (len(team_has_card) <= 1)
        if len(team_has_card) == 0:
            return Optional.empty()
        else:
            pair = {CARD: card, PLAYER: team_has_card.keys()[0]}
            declared_map.append(pair)

    return Optional(tuple(declared_map))


def get_eligible_question_pair(state: DataFrame, sets: tuple, opponents: tuple) -> (str, str):
    have = []
    might_have = []
    unknown = []
    does_not_have = []
    for card_set in sets:
        opponents_df = state.loc[list(card_set.value), list(opponents)]
        have_df = opponents_df[opponents_df[list(opponents)] == CardStatus.DOES_HAVE]
        have_for_set = list(have_df[have_df.notnull()].stack().index)

        might_have_df = opponents_df[opponents_df[list(opponents)] == CardStatus.MIGHT_HAVE]
        might_have_for_set = list(might_have_df[might_have_df.notnull()].stack().index)

        unknown_df = opponents_df[opponents_df[list(opponents)] == CardStatus.UNKNOWN]
        unknown_for_set = list(unknown_df[unknown_df.notnull()].stack().index)

        does_not_have_df = opponents_df[opponents_df[list(opponents)] == CardStatus.DOES_NOT_HAVE]
        does_not_have_for_set = list(does_not_have_df[does_not_have_df.notnull()].stack().index)

        have = have + have_for_set
        might_have = might_have + might_have_for_set
        unknown = unknown + unknown_for_set
        does_not_have = does_not_have + does_not_have_for_set

    logger.info(f'Computer Turn\nDoes Have: {len(have)}\nMight Have: {len(might_have)}\nUnknown: {len(unknown)}\nDoes Not Have: {len(does_not_have)}')
    if len(have) > 0:
        return random.choice(have)
    elif len(might_have) > 0:
        return random.choice(might_have)
    elif len(unknown) > 0:
        return random.choice(unknown)
    elif len(does_not_have) > 0:
        return random.choice(does_not_have)
    else:
        raise Exception('Could not find any cards to ask for. Should never happen')



