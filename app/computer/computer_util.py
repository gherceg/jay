from typing import Dict, List, Tuple

from pandas import DataFrame

from app.constants import *
from app.data.game import Game, Player
from app.data.game_enums import CardSet, CardStatus
from app.util import util_methods


def get_best_declaration_score(player: Player) -> Tuple[CardSet, int]:
    team_players = (player.name,) + player.teammates
    set_to_declare = None
    highest_score = -1
    for card_set in CardSet:
        score_for_set = score_declaration_for_set(player.state, team_players, card_set)
        if score_for_set > highest_score:
            highest_score = score_for_set
            set_to_declare = card_set

    return set_to_declare, highest_score


def score_declaration_for_set(state: DataFrame, team: tuple, card_set: CardSet) -> int:
    accumulated_score = 1
    for card in card_set.value:
        team_rows = state.loc[card, list(team)]
        team_has_card = team_rows[team_rows == CardStatus.DOES_HAVE]
        if len(team_has_card) == 0:
            team_might_have_card = team_rows[team_rows == CardStatus.MIGHT_HAVE]
            if len(team_might_have_card) == 0:
                team_unknown = team_rows[team_rows == CardStatus.UNKNOWN]
                if len(team_unknown) == 0:
                    accumulated_score *= 0
                else:
                    accumulated_score *= 1
            else:
                accumulated_score *= 2
        else:
            accumulated_score *= 3

    return accumulated_score


def declaration_to_dict(game: Game, name: str, card_set: CardSet, declared_map: List[Dict[str, str]]) -> Dict:
    return {
        MESSAGE_TYPE: DECLARATION,
        DATA: {
            PIN: game.pin,
            NAME: name,
            CARD_SET: util_methods.key_for_card_set(card_set),
            DECLARED_MAP: declared_map
        }
    }


def question_to_dict(game: Game, questioner: str, respondent: str, card: str) -> Dict:
    return {
        MESSAGE_TYPE: QUESTION,
        DATA: {
            PIN: game.pin,
            QUESTIONER: questioner,
            RESPONDENT: respondent,
            CARD: card
        }
    }
