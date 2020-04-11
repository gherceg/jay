import copy
import random
import logging

from app.game import Game
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
    game = Game(pin, network_delegate, players, teams, settings[VIRTUAL_DECK])

    player = get_first_turn(players)
    game.set_player_to_start(player)
    return game


def setup_teams(settings: dict) -> tuple:
    teams: list
    if TEAMS_KEY in settings:
        teams = settings[TEAMS_KEY]
    else:
        teams = generate_teams(settings[PLAYERS])
    return tuple(teams)


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
    team_one = tuple(copy.deepcopy(teams[0]['players']))
    team_two = tuple(copy.deepcopy(teams[1]['players']))
    if player_name in team_one:
        return team_two
    elif player_name in team_two:
        return team_one
    else:
        raise ValueError(f'Could not find team for player {player_name}')


def get_teammates(teams: tuple, player_name: str) -> tuple:
    if len(teams) != 2:
        raise ValueError('Only have support for 2 teams')
    team_one = copy.deepcopy(teams[0])
    team_two = copy.deepcopy(teams[1])
    if player_name in team_one[PLAYERS]:
        team_one[PLAYERS].remove(player_name)
        return tuple(team_one[PLAYERS])
    elif player_name in team_two[PLAYERS]:
        team_two[PLAYERS].remove(player_name)
        return tuple(team_two[PLAYERS])
    else:
        raise ValueError(f'Could not find team for player {player_name}')


def generate_teams(players: list) -> list:
    player_names = []
    for player in players:
        player_names.append(player[NAME])

    random.shuffle(player_names)
    # force int division
    half = len(player_names) // 2
    return [{'name': "Team 1", "players": player_names[:half]},
            {"name": "Team 2", "players": player_names[half:]}]


def get_first_turn(players: tuple) -> str:
    player_names = []
    for player in players:
        #TODO not capable of starting game with computer player yet
        if player.player_type == NETWORK_PLAYER:
            player_names.append(player.name)

    return random.choice(player_names)
