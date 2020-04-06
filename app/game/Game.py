from typing import Dict

from app.game.data.Turn import Turn
from app.game.data.Declaration import Declaration
from app.game.data.CardSet import CardSet
from app.player.QuestionDelegate import QuestionDelegate
from app.player.TurnDelegate import TurnDelegate
from app.network.NetworkDelegate import NetworkDelegate
from app.player.PlayerInterface import PlayerInterface
from app.Constants import *
from app.util.Optional import *


class Game(QuestionDelegate, TurnDelegate):
    """Responsible for managing a game and its players"""

    def __init__(self, network_delegate: NetworkDelegate, players: tuple, teams: tuple, virtual_deck: bool):
        self.network_delegate = network_delegate
        self.pin = 1234
        self.ledger = []
        self.up_next = None
        self.virtual_deck = virtual_deck

        # create a dictionary of players for easy lookup
        self.player_ids = {}
        self.players = {}
        for player in players:
            self.players[player.name] = player

        self.teams = {}
        for team in teams:
            self.teams[team[NAME]] = team[PLAYERS_KEY]

    async def handle_question(self, questioner: str, respondent: str, card: str):
        outcome = self.does_player_have_card(respondent, card)
        self.up_next = questioner if outcome else respondent
        turn = Turn(questioner, respondent, card, outcome)
        self.ledger.append(turn)
        for key, player in self.players.items():
            await player.received_next_turn(turn)

    async def handle_declaration(self, player: str, card_set: CardSet, declared_map: dict):
        outcome = True
        for (card, player) in declared_map.items():
            outcome = self.does_player_have_card(player, card) and outcome

        declaration = Declaration(player, card_set, declared_map, outcome)
        self.ledger.append(declaration)
        for key, player in self.players.items():
            await player.received_declaration(declaration)

    async def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        """Package update to send to client"""
        contents = game_update(self, self.players[player], Optional(turn))
        await self.network_delegate.broadcast_message(player, contents)

    async def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        """Package update to send to client"""
        contents = {}
        contents[MESSAGE_TYPE] = GAME_UPDATE
        contents[LAST_TURN] = declaration.to_dict()
        contents[CARDS] = cards
        contents[NEXT_TURN] = self.up_next
        contents[TEAMS_KEY] = self.build_teams_package()

        await self.network_delegate.broadcast_message(player, contents)

    def get_player_names(self):
        return list(self.players.keys())

    def get_teams_json(self) -> list:
        team_json = []
        for team_name, players in self.teams.items():
            team_players = []
            for player in players:
                player_data = {
                    NAME: player,
                    CARD_COUNT: len(self.players[player].get_cards())
                }
                team_players.append(player_data)

            team_entry = {NAME: team_name, PLAYERS_KEY: team_players}
            team_json.append(team_entry)
        return team_json

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


def game_update(game: Game, player: PlayerInterface,
                opt_turn: Optional[Turn] = Optional.empty()) -> Dict:
    contents = {
        MESSAGE_TYPE: GAME_UPDATE,
        DATA: {
            CARDS: player.get_cards(),
            NEXT_TURN: game.up_next,
            TEAMS_KEY: game.get_teams_json()
        }
    }

    if opt_turn.is_present():
        turn = opt_turn.get()
        contents[DATA][LAST_TURN] = {
            TYPE: TURN,
            DATA: turn.to_dict()
        }

    return contents
