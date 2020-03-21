import copy
import random

from app.game.Game import Game
from app.player.NetworkPlayer import NetworkPlayer
from app.player.ComputerPlayer import ComputerPlayer
from app.network.NetworkDelegate import NetworkDelegate
from app.util.UtilMethods import distribute_cards


class GameFactory:
    """Responsible for setting up a game and its players to a playable or near playable state depending on settings"""

    @staticmethod
    def create_game(network_delegate: NetworkDelegate, settings: dict) -> Game:
        """Given a dictionary containing game settings, setup a new game and create the players"""

        # create teams if necessary
        teams = GameFactory.setup_teams(settings)
        # create players
        players = GameFactory.setup_players(settings, teams)

        # if virtual deck has been specified, distribute cards now
        if settings['virtual_deck']:
            cards = distribute_cards(len(players))
            for player, hand in zip(players, cards):
                player.set_initial_cards(hand)

        game = Game(network_delegate, players, teams)

        # now that the game has been created, set appropriate delegates on players
        for player in players:
            if isinstance(player, NetworkPlayer):
                player.set_turn_delegate(game)
            elif isinstance(player, ComputerPlayer):
                player.set_question_delegate(game)

        return game

    @staticmethod
    def setup_teams(settings: dict) -> tuple:
        teams: list
        if 'teams' in settings:
            teams = settings['teams']
        else:
            teams = GameFactory.generate_teams(settings['players'])
        return tuple(teams)

    @staticmethod
    def setup_players(settings: dict, teams: tuple) -> tuple:
        """Set up each player and assign to teams"""

        all_players = []
        for player in settings['players']:
            all_players.append(player['name'])

        players = []
        for player in settings['players']:
            opposing_team = GameFactory.get_opposing_team(teams, player['name'])
            teammates = GameFactory.get_teammates(teams, player['name'])

            if player['type'] == 'network':
                player_to_add = NetworkPlayer(player['name'], teammates, opposing_team)
            elif player['type'] == 'computer':
                player_to_add = ComputerPlayer(player['name'], teammates, opposing_team)
            else:
                raise ValueError(f'Unrecognized player type key {player["type"]}')
            players.append(player_to_add)

        return tuple(players)

    @staticmethod
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

    @staticmethod
    def get_teammates(teams: tuple, player_name: str) -> tuple:
        if len(teams) != 2:
            raise ValueError('Only have support for 2 teams')
        team_one = copy.deepcopy(teams[0])
        team_two = copy.deepcopy(teams[1])
        if player_name in team_one['players']:
            team_one['players'].remove(player_name)
            return tuple(team_one['players'])
        elif player_name in team_two['players']:
            team_two['players'].remove(player_name)
            return tuple(team_two['players'])
        else:
            raise ValueError(f'Could not find team for player {player_name}')

    @staticmethod
    def generate_teams(players: list) -> list:
        player_names = []
        for player in players:
            player_names.append(player['name'])

        random.shuffle(player_names)
        # force int division
        half = len(player_names) // 2
        return [{'name': "Team 1", "players": player_names[:half]},
                {"name": "Team 2", "players": player_names[half:]}]

    