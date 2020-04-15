import copy
import random
import logging

from app.game import Game
from app.data import Player, Team
from app.player import PlayerInterface
from app.network import NetworkDelegate
from app.util import util_methods
from app.constants import *

logger = logging.getLogger(__name__)


def create_game(network_delegate: NetworkDelegate, settings: dict) -> Game:
    """Given a dictionary containing game settings, setup a new game and create the players"""

    # create teams if necessary
    teams = setup_teams(settings)
    # create players
    players = setup_players(settings, teams)

    # if virtual deck has been specified, distribute cards now
    if settings[VIRTUAL_DECK]:
        cards = util_methods.distribute_cards(len(players))
        for player, hand in zip(players, cards):
            player.set_initial_cards(hand)

    pin = random.randint(1000, 9999)

    teams_dict = {}
    for team in teams:
        teams_dict[team.name] = team
    game = Game(pin, network_delegate, players, teams_dict, settings[VIRTUAL_DECK])

    player = get_first_turn(players)
    game.set_player_to_start(player)
    return game


def setup_teams(settings: dict) -> tuple:
    if TEAMS_KEY in settings:
        teams = build_teams_from_settings(settings)
    else:
        teams = generate_teams(settings[PLAYERS])

    return teams


def setup_players(settings: dict, teams: tuple) -> tuple:
    """Set up each player and assign to teams"""

    all_players = []
    for player in settings[PLAYERS]:
        all_players.append(player[NAME])

    players = []
    for player in settings[PLAYERS]:
        opposing_team = get_opposing_team(teams, player[NAME])
        teammates = get_teammates(teams, player[NAME])
        player_type = player[PLAYER_TYPE]
        if player_type != NETWORK_PLAYER and player_type != COMPUTER_PLAYER:
            raise ValueError(f'Received invalid player type {player_type}')

        player_to_add = PlayerInterface(player[NAME], teammates, opposing_team, player_type)
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
    player_names = []
    for player in players:
        # TODO not capable of starting game with computer player yet
        if player.player_type == NETWORK_PLAYER:
            player_names.append(player.name)

    return random.choice(player_names)
