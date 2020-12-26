import logging
from typing import List

from app.data.game import Game, Player

logger = logging.getLogger(__name__)


def does_player_have_card(game: Game, player_name: str, card: str) -> bool:
    if player_name not in game.players.keys():
        raise ValueError(f"Player {player_name} not found in game")
    return game.players[player_name].has_card(card)


def get_opponents_names_in_play(game: Game, player: Player) -> List[str]:
    eligible_players = []
    for temp_player in game.players.values():
        if temp_player.team_name != player.team_name and temp_player.in_play:
            eligible_players.append(temp_player.name)

    return eligible_players


def get_opposing_team_name_for_player(game: Game, player: str) -> str:
    for team in game.teams.values():
        if player not in team.player_names:
            return team.name


def is_game_over(game: Game) -> bool:
    total_sets_won = 0
    for team in game.teams.values():
        total_sets_won += team.sets_won

    logger.info(f'Total sets won: {total_sets_won}')
    return total_sets_won == 8


def get_opponents_in_play(game: Game, player: Player) -> List[Player]:
    eligible_players = []
    for temp_player in game.players.values():
        if temp_player.team_name != player.team_name and temp_player.in_play:
            eligible_players.append(temp_player)

    return eligible_players


def get_teammates_in_play(game: Game, player: Player) -> List[Player]:
    eligible_players = []
    for temp_player in game.players.values():
        logger.info(f'Finding eligible teammates: {temp_player.name} on team {temp_player.team_name}')
        if temp_player.team_name == player.team_name and temp_player.in_play:
            eligible_players.append(temp_player)

    return eligible_players
