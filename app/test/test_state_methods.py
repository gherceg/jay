from app.player.StateMethods import StateMethods
from app.game.data.CardStatus import CardStatus
from app.util.DataFrameMethods import *
from app.util.UtilMethods import *


# Tests for create_default_state() method


def test_default_state_row_count():
    players = ["a", "b", "c"]
    expected_row_count = 0
    for card_set in CardSet:
        expected_row_count += len(card_set.value)
    state: DataFrame = StateMethods.create_default_state(players)
    actual_row_count = len(state)
    assert expected_row_count == actual_row_count


def test_default_state_column_count():
    players = ["a", "b", "c"]
    expected_column_count = len(players)

    state: DataFrame = StateMethods.create_default_state(players)
    actual_column_count = len(state.columns)
    assert expected_column_count == actual_column_count


def test_default_state_values():
    players = ("a", "b", "c")

    state: DataFrame = StateMethods.create_default_state(players)
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
    state: DataFrame = StateMethods.create_default_state(players)
    state = StateMethods.update_state_upon_receiving_cards(state, 'a', cards)
    for card in deck_of_cards():
        if card in cards:
            assert state.loc[card, 'a'] == CardStatus.DOES_HAVE
        else:
            assert state.loc[card, 'a'] == CardStatus.DOES_NOT_HAVE
