from app.player import NetworkPlayer
from app.player import state_methods


def test_get_cards():
    expected_cards = ('2s', '4c', '9h', 'ad')
    player = NetworkPlayer('a', ('what', 'ever'), ('doesnt', 'matter', 'at all'))

    state = state_methods.update_state_upon_receiving_cards(player.state, 'a', expected_cards)
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
    player = NetworkPlayer('a', ('what', 'ever'), ('doesnt', 'matter', 'at all'))

    # test
    state = state_methods.update_state_upon_receiving_cards(player.state, 'a', expected_cards)
    player.state = state

    # assert
    has_card = player.has_card('2s')
    assert has_card


def test_has_card_is_false():
    expected_cards = ('2s', '4c', '9h', 'ad')
    player = NetworkPlayer('a', ('what', 'ever'), ('doesnt', 'matter', 'at all'))

    state = state_methods.update_state_upon_receiving_cards(player.state, 'a', expected_cards)
    player.state = state

    has_card = player.has_card('2c')
    assert not has_card
