from typing import Dict
import logging

from app.constants import *
from app.game import Game
from app.player import PlayerInterface
from app.game.data import Turn, Declaration
from app.util import Optional

logger = logging.getLogger(__name__)


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
            TEAMS_KEY: formatted_teams(game)
        }
    }


def game_update(game: Game, player: PlayerInterface) -> Dict:
    opt_turn = Optional(game.ledger[-1]) if len(game.ledger) > 0 else Optional.empty()
    contents = {
        MESSAGE_TYPE: GAME_UPDATE,
        DATA: {
            PLAYER: {
                NAME: player.name,
                CARDS: player.get_cards()
            },
            NEXT_TURN: game.up_next.get() if game.up_next.is_present() else '',
            TEAMS_KEY: formatted_teams(game)
        }
    }

    if opt_turn.is_present():
        turn = opt_turn.get()
        turn_type = TURN if isinstance(turn, Turn) else DECLARATION
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
    for team_name, players in game.teams.items():
        team_players = []
        for player in players:
            player_data = {
                NAME: player,
                CARD_COUNT: game.get_player_card_count(player)
            }
            team_players.append(player_data)

        team_entry = {NAME: team_name, PLAYERS: team_players, SET_COUNT: game.set_counts[team_name]}
        team_json.append(team_entry)
    return team_json
