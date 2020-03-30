from app.game.data.Turn import Turn
from app.game.data.Declaration import Declaration
from app.game.data.CardSet import CardSet
from app.player.QuestionDelegate import QuestionDelegate
from app.player.TurnDelegate import TurnDelegate
from app.network.NetworkDelegate import NetworkDelegate
from app.Constants import *


class Game(QuestionDelegate, TurnDelegate):
    """Responsible for managing a game and its players"""

    def __init__(self, network_delegate: NetworkDelegate, players: tuple, teams: tuple):
        self.network_delegate = network_delegate
        self.pin = 1234
        self.ledger = []

        # create a dictionary of players for easy lookup
        self.player_ids = {}
        self.players = {}
        for player in players:
            self.players[player.name] = player

        self.teams = {}
        for team in teams:
            self.teams[team[NAME]] = team[PLAYERS_KEY]

    def handle_question(self, questioner: str, respondent: str, card: str):
        outcome = self.does_player_have_card(respondent, card)
        turn = Turn(questioner, respondent, card, outcome)
        self.ledger.append(turn)
        for key, player in self.players.items():
            player.received_next_turn(turn)

    def handle_declaration(self, player: str, card_set: CardSet, declared_map: dict):
        # convert string card set to enum

        outcome = True
        for (card, player) in declared_map.items():
            outcome = self.does_player_have_card(player, card) and outcome

        declaration = Declaration(player, card_set, declared_map, outcome)
        self.ledger.append(declaration)
        for key, player in self.players.items():
            player.received_declaration(declaration)

    def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        """Package update to send to client"""
        contents = {}
        contents[MESSAGE_TYPE] = GAME_UPDATE
        contents[LAST_TURN] = turn.to_dict()
        contents[CARDS] = cards
        # contents['current_turn'] = self.game.up_next
        contents[TEAMS_KEY] = self.build_teams_package()

        self.network_delegate.broadcast_message(player, contents)

    def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        """Package update to send to client"""
        contents = {}
        contents[MESSAGE_TYPE] = GAME_UPDATE
        contents[LAST_TURN] = declaration.to_dict()
        contents[CARDS] = cards
        # contents['current_turn'] = self.game.up_next
        contents[TEAMS_KEY] = self.build_teams_package()

        self.network_delegate.broadcast_message(player, contents)

    def get_player_names(self):
        return list(self.players.keys())

    # PRIVATE METHODS

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.players[player_name].has_card(card)

    def build_teams_package(self) -> dict:
        teams_dict = {}
        for name, players in self.teams.items():
            team_players = []
            for player_name in players:
                player_dict = {
                    NAME: player_name,
                    CARD_COUNT: len(self.players[player_name].get_cards())
                }
                team_players.append(player_dict)
            teams_dict[name] = team_players
        return teams_dict
