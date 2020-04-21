import logging
from pandas import DataFrame
import random
from typing import List

from app.data import Question, Declaration, CardStatus, CardSet
from app.util import util_methods, data_frame_methods, Optional
from app.constants import *

logger = logging.getLogger(__name__)


def create_default_state(players: List[str]) -> DataFrame:
    """Creates and returns a DataFrame object that contains a column for each player and a row for each card
        Each cell is set to the CardStatus UNKNOWN
    """
    cards = util_methods.deck_of_cards()
    return data_frame_methods.create_state_with_value(cards, players, CardStatus.UNKNOWN)


def update_player_state_for_question(state: DataFrame, question: Question, players_out: List[str]) -> DataFrame:
    state = update_state_with_turn(state, question)
    state = update_state_with_players_out_of_cards(state, players_out)
    state = check_for_process_of_elimination(state)
    return state


def update_player_state_for_declaration(state: DataFrame, declaration: Declaration, players_out: List[str]) -> DataFrame:
    state = update_state_with_declaration(state, declaration)
    state = update_state_with_players_out_of_cards(state, players_out)
    state = check_for_process_of_elimination(state)
    return state


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


def update_state_with_turn(state: DataFrame, question: Question) -> DataFrame:
    card_set: CardSet = util_methods.set_for_card(question.card)

    if question.outcome:
        # the questioner has the card so the rest do not
        state.loc[question.card, :] = CardStatus.DOES_NOT_HAVE
        state.loc[question.card, question.questioner] = CardStatus.DOES_HAVE
    else:
        # both players do not have the given card
        state.loc[question.card, question.questioner] = CardStatus.DOES_NOT_HAVE
        state.loc[question.card, question.respondent] = CardStatus.DOES_NOT_HAVE

    # update any unknown statuses to might have for the player asking the question
    state = data_frame_methods.update_rows_with_old_to_new_for_column(state,
                                                                      card_set.value,
                                                                      question.questioner,
                                                                      CardStatus.UNKNOWN,
                                                                      CardStatus.MIGHT_HAVE)

    return state


def update_state_with_declaration(state: DataFrame, declaration: Declaration) -> DataFrame:
    for player_card_pair in declaration.declared_list:
        state.loc[player_card_pair[CARD], :] = CardStatus.DECLARED

    return state


def update_state_with_players_out_of_cards(state: DataFrame, players: List[str]) -> DataFrame:
    # for each player specified, ensure all values are DECLARED or DOES_NOT_HAVE
    cards = util_methods.deck_of_cards()
    for player in players:
        # update all values for a player to does not have unless value is declared
        state = data_frame_methods.update_rows_not_with_old_to_new_for_column(state, cards, player, CardStatus.DECLARED,
                                                                              CardStatus.DOES_NOT_HAVE)
    return state


def check_for_process_of_elimination(state: DataFrame) -> DataFrame:
    for card in util_methods.deck_of_cards():
        state = process_of_elimination(state, card)
    return state


def process_of_elimination(state: DataFrame, row: str) -> DataFrame:
    status_for_card = state.loc[row, :]
    does_not_have_count = len(status_for_card.where(status_for_card == CardStatus.DOES_NOT_HAVE).dropna())
    leftover_columns = status_for_card.where(status_for_card != CardStatus.DOES_NOT_HAVE).dropna()
    if does_not_have_count == len(state.columns) - 1 and (
            leftover_columns[0] != CardStatus.DOES_HAVE and leftover_columns[0] != CardStatus.DECLARED):
        if len(leftover_columns) != 1:
            raise Exception('Should not be possible')
        column_to_update = leftover_columns.index[0]
        state = data_frame_methods.update_rows_to_value_for_column(state, (row,), column_to_update,
                                                                   CardStatus.DOES_HAVE)
    return state


# Read Methods
def get_cards_for_player(state: DataFrame, player: str) -> List[str]:
    card_rows = state.loc[:, player]
    cards = card_rows[card_rows == CardStatus.DOES_HAVE]
    return list(cards.keys())


def get_players_out_of_cards(state: DataFrame) -> List[str]:
    players = []
    for player_name in state.columns.tolist():
        if len(get_cards_for_player(state, player_name)) == 0:
            players.append(player_name)

    return players


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
