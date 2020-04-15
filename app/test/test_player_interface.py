from app.player import PlayerInterface
from app import game_state
from app.constants import *


def test_get_cards():
    expected_cards = ('2s', '4c', '9h', 'ad')
    player = PlayerInterface('a', ('what', 'ever'), ('doesnt', 'matter', 'at all'), NETWORK_PLAYER)

    state = game_state.update_state_upon_receiving_cards(player.state, 'a', expected_cards)
    player.state = state

    actual_cards = player.get_cards()
    mutable_actual_cards = list(actual_cards)
    # NOTE: order is different, so making sure elements are the same
    for card in expected_cards:
        assert card in mutable_actual_cards
        mutable_actual_cards.remove(card)

    assert not mutable_actual_cards


def test_has_card_is_true():
    # setup
    expected_cards = ('2s', '4c', '9h', 'ad')
    player = PlayerInterface('a', ('what', 'ever'), ('doesnt', 'matter', 'at all'), NETWORK_PLAYER)

    # test
    state = game_state.update_state_upon_receiving_cards(player.state, 'a', expected_cards)
    player.state = state

    # assert
    has_card = player.has_card('2s')
    assert has_card


def test_has_card_is_false():
    expected_cards = ('2s', '4c', '9h', 'ad')
    player = PlayerInterface('a', ('what', 'ever'), ('doesnt', 'matter', 'at all'), NETWORK_PLAYER)

    state = game_state.update_state_upon_receiving_cards(player.state, 'a', expected_cards)
    player.state = state

    has_card = player.has_card('2c')
    assert not has_card
