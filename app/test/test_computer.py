import logging

from pandas import DataFrame

from app.computer import simple_computer
from app.constants import *
from app.data.game_enums import CardSet, CardStatus
from app.gameplay import game_state_methods
from app.util import data_frame_methods, util_methods

logger = logging.getLogger(__name__)


def test_eligible():
    players = ['a', 'b', 'c']
    cards_for_a = ['2s', '7h']
    cards_for_b = ['4s', '3d']
    cards_for_c = ['2h', '3h']

    state: DataFrame = game_state_methods.create_default_state(players)
    state = data_frame_methods.update_rows_to_value_for_column(state, cards_for_a, 'a', CardStatus.MIGHT_HAVE)
    state = data_frame_methods.update_rows_to_value_for_column(state, cards_for_b, 'b', CardStatus.DOES_HAVE)
    state = game_state_methods.update_state_upon_receiving_cards(state, 'c', cards_for_c)

    players_to_ask = ['a', 'b']
    cards_to_ask = util_methods.eligible_cards(cards_for_c)
    card, player = simple_computer.get_eligible_question_pair(state, cards_to_ask, players_to_ask)
    assert card in cards_to_ask
    assert player in players_to_ask
    assert player == 'a'
    assert card == '7h'


def test_declaration_check():
    players = ["a", "b", "c"]
    cards_for_a = ['2s', '4s']
    cards_for_b = ['3s', '5s']
    cards_for_c = ['6s', '7s']
    expected_declared_map = [{CARD: '2s', PLAYER: 'a'},
                             {CARD: '3s', PLAYER: 'b'},
                             {CARD: '4s', PLAYER: 'a'},
                             {CARD: '5s', PLAYER: 'b'},
                             {CARD: '6s', PLAYER: 'c'},
                             {CARD: '7s', PLAYER: 'c'}]

    state: DataFrame = game_state_methods.create_default_state(players)
    state = game_state_methods.update_state_upon_receiving_cards(state, 'a', cards_for_a)
    state = game_state_methods.update_state_upon_receiving_cards(state, 'b', cards_for_b)
    state = game_state_methods.update_state_upon_receiving_cards(state, 'c', cards_for_c)

    # check declaration
    opt_declared_map = game_state_methods.able_to_declare(state, players, CardSet.LOW_SPADES)

    assert (opt_declared_map.is_present())
    assert expected_declared_map == opt_declared_map.get()
