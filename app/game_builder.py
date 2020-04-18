import copy
import random
import logging
from pandas import DataFrame

from app.game import Game
from app.data import Player, Team
from app.network import NetworkDelegate
from app.util import util_methods
from app.constants import *
import app.game_state as game_state

logger = logging.getLogger(__name__)


def create_game(network_delegate: NetworkDelegate, settings: dict) -> Game:
    """Given a dictionary containing game settings, setup a new game and create the players"""

    player_names = []
    for player in settings[PLAYERS]:
        player_names.append(player[NAME])

    # create teams if necessary
    teams = setup_teams(settings)
    # create default state
    default_state = game_state.create_default_state(tuple(player_names))
    # create players
    players = setup_players(settings, teams, default_state)

    # if virtual deck has been specified, distribute cards now
    if settings[VIRTUAL_DECK]:
        cards = util_methods.distribute_cards(len(players))
        for player, hand in zip(players, cards):
            logger.info(f'Setting initial cards for {player.name} to {hand}')
            logger.info(f'Building: Player {player.name} located at {id(player)}')
            player.state = game_state.update_state_upon_receiving_cards(player.state, player.name, hand)

    pin = random.randint(1000, 9999)

    teams_dict = {}
    for team in teams:
        teams_dict[team.name] = team
    game = Game(pin, network_delegate, players, teams_dict, settings[VIRTUAL_DECK])

    player_name: str = get_first_turn(players)
    game.set_player_to_start(player_name)
    return game


def setup_teams(settings: dict) -> tuple:
    if TEAMS_KEY in settings:
        teams = build_teams_from_settings(settings)
    else:
        teams = generate_teams(settings[PLAYERS])

    return teams


def setup_players(settings: dict, teams: tuple, default_state: DataFrame) -> tuple:
    """Set up each player and assign to teams"""

    players = []
    for player in settings[PLAYERS]:
        opposing_team = get_opposing_team(teams, player[NAME])
        teammates = get_teammates(teams, player[NAME])
        player_type = player[PLAYER_TYPE]
        logger.info(f'setting up {player[NAME]}: {teammates} vs {opposing_team}')
        if player_type != NETWORK_PLAYER and player_type != COMPUTER_PLAYER:
            raise ValueError(f'Received invalid player type {player_type}')
        player_to_add = Player(player[NAME], player[TYPE], player[TEAM], teammates, opposing_team, copy.deepcopy(default_state))
        players.append(player_to_add)

    return tuple(players)


def get_opposing_team(teams: tuple, player_name: str) -> tuple:
    if len(teams) != 2:
        raise ValueError('Only have support for 2 teams')
    team_one = tuple(copy.deepcopy(teams[0].player_names))
    team_two = tuple(copy.deepcopy(teams[1].player_names))
    if player_name in team_one:
        return team_two
    elif player_name in team_two:
        return team_one
    else:
        raise ValueError(f'Could not find team for player {player_name}')


def get_teammates(teams: tuple, player_name: str) -> tuple:
    if len(teams) != 2:
        raise ValueError('Only have support for 2 teams')
    team_one_players = list(copy.deepcopy(teams[0].player_names))
    team_two_players = list(copy.deepcopy(teams[1].player_names))
    if player_name in team_one_players:
        team_one_players.remove(player_name)
        return tuple(team_one_players)
    elif player_name in team_two_players:
        team_two_players.remove(player_name)
        return tuple(team_two_players)
    else:
        raise ValueError(f'Could not find team for player {player_name}')


def build_teams_from_settings(settings: dict) -> tuple:
    teams_from_settings = settings[TEAMS_KEY]
    teams = []
    for team_entry in teams_from_settings:
        logger.info(f'Creating team {team_entry[NAME]}')
        temp_team = Team(team_entry[NAME], team_entry[PLAYERS], 0)
        teams.append(temp_team)

    return tuple(teams)


def generate_teams(players: list) -> tuple:
    player_names = []
    for player in players:
        player_names.append(player[NAME])

    random.shuffle(player_names)
    # force int division
    half = len(player_names) // 2
    # return [{'name': "Team 1", "players": player_names[:half]},
    #         {"name": "Team 2", "players": player_names[half:]}]
    return Team("Team 1", tuple(player_names[:half]), 0), Team("Team 2", tuple(player_names[half:]), 0)


def get_first_turn(players: tuple) -> str:
    network_players = filter(lambda p: p.player_type == NETWORK_PLAYER, players)
    player_names = map(lambda p: p.name, list(network_players))
    return random.choice(list(player_names))
