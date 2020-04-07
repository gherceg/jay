from app.util import util_methods
from app.game.data import CardSet


# Tests for set_for_card(card) util method
def test_valid_card_for_set_returns_high_hearts():
    card = "ah"
    expected_card_set = CardSet.HIGH_HEARTS
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_high_spades():
    card = "as"
    expected_card_set = CardSet.HIGH_SPADES
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_high_clubs():
    card = "ac"
    expected_card_set = CardSet.HIGH_CLUBS
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_high_diamonds():
    card = "ad"
    expected_card_set = CardSet.HIGH_DIAMONDS
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_low_spades():
    card = "2s"
    expected_card_set = CardSet.LOW_SPADES
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_low_clubs():
    card = "2c"
    expected_card_set = CardSet.LOW_CLUBS
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_low_diamonds():
    card = "2d"
    expected_card_set = CardSet.LOW_DIAMONDS
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_valid_card_for_set_returns_low_hearts():
    card = "2h"
    expected_card_set = CardSet.LOW_HEARTS
    actual_card_set = util_methods.set_for_card(card)
    assert expected_card_set == actual_card_set


def test_invalid_card_for_set_returns_exception():
    card = "dq"
    try:
        card_set = util_methods.set_for_card(card)
    except ValueError:
        assert True
    else:
        assert False


# Test distribute cards
def test_distribute_cards():
    cards = util_methods.distribute_cards(6)
    # verify that all hands are unique
    complete_deck = util_methods.deck_of_cards()
    actual_deck = []
    for hand in cards:
        for card in hand:
            # assert card is valid
            assert card in complete_deck
            # assert card is unique̵
            assert card not in actual_deck
            # add to actual deck
            actual_deck.append(card)

    assert len(actual_deck) == 48


def test_distribute_cards_raises_exception():
    try:
        cards = util_methods.distribute_cards(10)
    except ValueError:
        assert True
    else:
        assert False
