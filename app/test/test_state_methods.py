from pandas import Series, DataFrame
import logging

# TODO: currently dependent on importing Server first, understand why order matters for your imports
from app.network import Server
from app.player import state_methods
from app.util import data_frame_methods
from app.util import util_methods
from app.game.data import CardStatus, CardSet
from app.constants import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# Tests for create_default_state() method


def test_default_state_row_count():
    players = ("a", "b", "c")
    expected_row_count = 0
    for card_set in CardSet:
        expected_row_count += len(card_set.value)
    state: DataFrame = state_methods.create_default_state(players)
    actual_row_count = len(state)
    assert expected_row_count == actual_row_count


def test_default_state_column_count():
    players = ("a", "b", "c")
    expected_column_count = len(players)

    state: DataFrame = state_methods.create_default_state(players)
    actual_column_count = len(state.columns)
    assert expected_column_count == actual_column_count


def test_default_state_values():
    players = ("a", "b", "c")

    state: DataFrame = state_methods.create_default_state(players)
    series_a: Series = state["a"].value_counts()
    series_b: Series = state["b"].value_counts()
    series_c: Series = state["c"].value_counts()

    # Assert that each column has 48 rows, all set to UNKNOWN
    assert series_a[0] == 48
    assert series_a.keys()[0] == CardStatus.UNKNOWN
    assert series_b[0] == 48
    assert series_b.keys()[0] == CardStatus.UNKNOWN
    assert series_c[0] == 48
    assert series_c.keys()[0] == CardStatus.UNKNOWN


def test_update_state_for_cards():
    players = ('a', 'b', 'c')
    cards = ('2s', '4c', '9h', 'ad')
    state: DataFrame = state_methods.create_default_state(players)
    state = state_methods.update_state_upon_receiving_cards(state, 'a', cards)
    for card in util_methods.deck_of_cards():
        if card in cards:
            assert state.loc[card, 'a'] == CardStatus.DOES_HAVE
        else:
            assert state.loc[card, 'a'] == CardStatus.DOES_NOT_HAVE


def test_declaration_check():
    players = ('a', 'b', 'c')
    cards_for_a = ('2s', '4s')
    cards_for_b = ('3s', '5s')
    cards_for_c = ('6s', '7s')
    expected_declared_map = ({CARD: '2s', PLAYER: 'a'},
                             {CARD: '3s', PLAYER: 'b'},
                             {CARD: '4s', PLAYER: 'a'},
                             {CARD: '5s', PLAYER: 'b'},
                             {CARD: '6s', PLAYER: 'c'},
                             {CARD: '7s', PLAYER: 'c'})

    state: DataFrame = state_methods.create_default_state(players)
    state = state_methods.update_state_upon_receiving_cards(state, 'a', cards_for_a)
    state = state_methods.update_state_upon_receiving_cards(state, 'b', cards_for_b)
    state = state_methods.update_state_upon_receiving_cards(state, 'c', cards_for_c)

    # check declaration
    opt_declared_map = state_methods.able_to_declare(state, players, CardSet.LOW_SPADES)

    assert (opt_declared_map.is_present())
    assert expected_declared_map == opt_declared_map.get()


def test_eligible():
    players = ('a', 'b', 'c')
    cards_for_a = ('2s', '3s')
    cards_for_b = ('4s', '3d')
    cards_for_c = ('2h', '3h')

    state: DataFrame = state_methods.create_default_state(players)
    state = data_frame_methods.update_rows_to_value_for_column(state, cards_for_a, 'a', CardStatus.MIGHT_HAVE)
    state = data_frame_methods.update_rows_to_value_for_column(state, cards_for_b, 'b', CardStatus.DOES_HAVE)
    state = state_methods.update_state_upon_receiving_cards(state, 'c', cards_for_c)

    card, player = state_methods.get_eligible_question_pair(state, (CardSet.LOW_SPADES,), players)
    assert player == 'b'
    assert card in '4s'
