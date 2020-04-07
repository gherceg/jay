from typing import Dict

from app.constants import *
from app.game import Game
from app.player import PlayerInterface
from app.game.data import Turn, Declaration
from app.util import Optional


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


def game_update(game: Game, player: PlayerInterface,
                opt_turn: Optional[Turn] = Optional.empty()) -> Dict:
    contents = {
        MESSAGE_TYPE: GAME_UPDATE,
        DATA: {
            PLAYER: {
                NAME: player.name,
                CARDS: player.get_cards()
            },
            NEXT_TURN: game.up_next,
            TEAMS_KEY: formatted_teams(game)
        }
    }

    if opt_turn.is_present():
        turn = opt_turn.get()
        contents[DATA][LAST_TURN] = {
            TYPE: TURN,
            DATA: turn.to_dict()
        }

    return contents


def game_update_for_declaration(game: Game, player: PlayerInterface, declaration: Declaration) -> Dict:
    contents = {
        MESSAGE_TYPE: GAME_UPDATE,
        DATA: {
            PLAYER: {
                NAME: player.name,
                CARDS: player.get_cards()
            },            NEXT_TURN: game.up_next,
            TEAMS_KEY: formatted_teams(game),
            LAST_TURN: {
                TYPE: DECLARATION,
                DATA: declaration.to_dict()
            }
        }
    }

    return contents


def formatted_teams(game: Game) -> list:
    team_json = []
    for team_name, players in game.teams.items():
        team_players = []
        for player in players:
            player_data = {
                NAME: player,
                CARD_COUNT: len(game.players[player].get_cards())
            }
            team_players.append(player_data)

        team_entry = {NAME: team_name, PLAYERS: team_players, SET_COUNT: game.set_counts[team_name]}
        team_json.append(team_entry)
    return team_json
