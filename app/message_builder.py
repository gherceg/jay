from typing import Dict
import logging

from app.constants import *
from app.data.game import Game, Player
from app.data.turn import Question, Declaration
from app.util import Optional

logger = logging.getLogger(__name__)


def error(message: str) -> Dict:
    logger.error(message)
    return {
        MESSAGE_TYPE: ERROR,
        DATA: {
            DESCRIPTION: message
        }
    }


def created_game(game: Game) -> Dict:
    return {
        MESSAGE_TYPE: CREATED_GAME,
        DATA: {
            PIN: game.pin,
        }
    }


def joined_game(game: Game) -> Dict:
    return {
        MESSAGE_TYPE: JOINED_GAME,
        DATA: {
            PIN: game.pin,
            TEAMS_KEY: formatted_teams(game)
        }
    }


def game_update(game: Game, player: Player) -> Dict:
    opt_turn = Optional(game.ledger[-1]) if len(game.ledger) > 0 else Optional.empty()
    contents = {
        MESSAGE_TYPE: GAME_UPDATE,
        DATA: {
            PIN: game.pin,
            PLAYER: {
                NAME: player.name,
                CARDS: player.get_cards()
            },
            NEXT_TURN: game.player_up_next.get() if game.player_up_next.is_present() else '',
            TEAMS_KEY: formatted_teams(game)
        }
    }

    if opt_turn.is_present():
        # could be instance of Question or Declaration
        turn = opt_turn.get()
        turn_type = TURN if isinstance(turn, Question) else DECLARATION
        contents[DATA][LAST_TURN] = {
            TYPE: turn_type,
            DATA: turn.to_dict()
        }

    return contents


def end_game(game: Game) -> Dict:
    return {
        MESSAGE_TYPE: END_GAME,
        DATA: {
            TEAMS_KEY: formatted_teams(game)
        }
    }


def formatted_teams(game: Game) -> list:
    team_json = []
    for team in game.teams.values():
        team_players = []
        for player_name in team.player_names:
            player: Player = game.players[player_name]
            player_data = {
                NAME: player.name,
                TYPE: player.player_type,
                CARD_COUNT: len(player.get_cards())
            }
            team_players.append(player_data)

        team_entry = {NAME: team.name, PLAYERS: team_players, SET_COUNT: team.sets_won}
        team_json.append(team_entry)
    return team_json
