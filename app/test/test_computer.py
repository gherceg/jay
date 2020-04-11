import logging
from pandas import DataFrame

from app.player import state_methods, computer_player_methods as cpm
from app.util import data_frame_methods, util_methods
from app.game.data import CardStatus, CardSet

logger = logging.getLogger(__name__)


def test_eligible():
    players = ('a', 'b', 'c')
    cards_for_a = ('2s', '3s')
    cards_for_b = ('4s', '3d')
    cards_for_c = ('2h', '3h')

    state: DataFrame = state_methods.create_default_state(players)
    state = data_frame_methods.update_rows_to_value_for_column(state, cards_for_a, 'a', CardStatus.MIGHT_HAVE)
    state = data_frame_methods.update_rows_to_value_for_column(state, cards_for_b, 'b', CardStatus.DOES_HAVE)
    state = state_methods.update_state_upon_receiving_cards(state, 'c', cards_for_c)

    cards_to_ask = util_methods.eligible_cards(cards_for_c)
    card, player = cpm.get_eligible_question_pair(state, cards_to_ask, players)
    assert player == 'b'
    assert card in '4s'
