import logging
import random
from typing import Dict, List

from pandas import DataFrame

from app.computer import computer_util
from app.constants import *
from app.data.game import Game, Player
from app.data.game_enums import CardSet, CardStatus
from app.gameplay import game_state_methods
from app.util import util_methods

logger = logging.getLogger(__name__)


def generate_turn(player: Player, eligible_player_names: List[str], game: Game) -> Dict:
    set_to_declare, score = computer_util.get_best_declaration_score(player)
    logger.info(f'Best set to declare is {set_to_declare} with a score of {score}')

    if len(eligible_player_names) == 0:
        # have to declare
        return attempt_to_declare(player, game)

    # first check if computer knows where all of the cards of a certain set are
    team_players = (player.name,) + player.teammates
    for card_set in CardSet:
        declared_map = game_state_methods.able_to_declare(player.state, team_players, card_set)
        if declared_map:
            return computer_util.declaration_to_dict(game, player.name, card_set, declared_map)

    # could not declare, so ask a question
    eligible_cards = util_methods.eligible_cards(player.get_cards())
    logger.debug(f'Eligible players names: {eligible_player_names}')
    card, player_to_ask = get_eligible_question_pair(player.state, eligible_cards, eligible_player_names)
    if card is not None and player_to_ask is not None:
        return computer_util.question_to_dict(game, player.name, player_to_ask, card)
    else:
        return attempt_to_declare(player, game)


def attempt_to_declare(player: Player, game: Game) -> Dict:
    team = [player.name] + player.teammates
    set_to_declare, score = computer_util.get_best_declaration_score(player)
    declared_map: List[Dict[str, str]] = declare(player, team, set_to_declare)
    return computer_util.declaration_to_dict(game, player.name, set_to_declare, declared_map)


def declare(player: Player, team: List[str], set_to_declare: CardSet) -> List[Dict[str, str]]:
    declared_list = []
    for card in set_to_declare.value:
        team_rows = player.state.loc[card, team]
        player_for_card = None
        team_has_card = team_rows[team_rows == CardStatus.DOES_HAVE]
        if len(team_has_card) == 0:
            team_might_have_card = team_rows[team_rows == CardStatus.MIGHT_HAVE]
            if len(team_might_have_card) == 0:
                team_unknown = team_rows[team_rows == CardStatus.UNKNOWN]
                if len(team_unknown) == 0:
                    team_does_not_have = team_rows[team_rows == CardStatus.DOES_NOT_HAVE]
                    logger.error(
                        f'Computer is being forced to declare even though it is not possible. Should not happen.\n\{player.get_cards()}n{player.state}')
                    player_for_card = team_does_not_have.keys()[0]
                else:
                    player_for_card = team_unknown.keys()[0]
            else:
                player_for_card = team_might_have_card.keys()[0]
        else:
            player_for_card = team_has_card.keys()[0]

        pair = {CARD: card, PLAYER: player_for_card}
        declared_list.append(pair)

    return declared_list


def get_eligible_question_pair(state: DataFrame, cards_to_ask_for: List[str], opponents: List[str]) -> (str, str):
    opponents_df = state.loc[cards_to_ask_for, opponents]

    have_df = opponents_df[opponents_df[opponents] == CardStatus.DOES_HAVE]
    have = list(have_df[have_df.notnull()].stack().index)

    might_have_df = opponents_df[opponents_df[opponents] == CardStatus.MIGHT_HAVE]
    might_have = list(might_have_df[might_have_df.notnull()].stack().index)

    unknown_df = opponents_df[opponents_df[opponents] == CardStatus.UNKNOWN]
    unknown = list(unknown_df[unknown_df.notnull()].stack().index)

    does_not_have_df = opponents_df[opponents_df[opponents] == CardStatus.DOES_NOT_HAVE]
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