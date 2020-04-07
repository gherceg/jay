import logging

from app.game.data import Turn, Declaration, CardSet
from app.player import TurnDelegate, QuestionDelegate, state_methods
from app.network import NetworkDelegate
from app.constants import *
from app.util import Optional
from app.game import game_messages

logger = logging.getLogger(__name__)


class Game(QuestionDelegate, TurnDelegate):
    """Responsible for managing a game and its players"""

    def __init__(self, network_delegate: NetworkDelegate, players: tuple, teams: tuple, virtual_deck: bool):
        self.network_delegate = network_delegate
        self.pin = 1234
        self.ledger = []
        self.up_next = None
        self.state = None
        self.virtual_deck = virtual_deck

        # create a dictionary of players for easy lookup
        self.players = {}
        for player in players:
            self.players[player.name] = player

        self.teams = {}
        for team in teams:
            self.teams[team[NAME]] = team[PLAYERS]

        self.set_counts = {}
        for team in teams:
            self.set_counts[team[NAME]] = 0

        self.setup_state()

    async def handle_question(self, questioner: str, respondent: str, card: str):
        outcome = self.does_player_have_card(respondent, card)
        self.up_next = questioner if outcome else respondent
        turn = Turn(questioner, respondent, card, outcome)
        self.state = state_methods.update_state_with_turn(self.state, turn)
        self.ledger.append(turn)
        for key, player in self.players.items():
            await player.received_next_turn(turn)

    async def handle_declaration(self, player: str, card_set: CardSet, declared_map: dict):
        outcome = True
        for (card, player) in declared_map.items():
            outcome = self.does_player_have_card(player, card) and outcome

        # TODO not the most elegant way to do this
        team_name = self.get_team_for_player(player) if outcome else self.get_opposing_team_for_player(player)
        self.set_counts[team_name] += 1

        declaration = Declaration(player, card_set, declared_map, outcome)
        self.state = state_methods.update_state_with_declaration(self.state, declaration)
        self.ledger.append(declaration)
        for key, player in self.players.items():
            await player.received_declaration(declaration)

    # TurnDelegate Methods
    async def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        contents = game_messages.game_update(self, self.players[player], Optional(turn))
        await self.network_delegate.broadcast_message(player, contents)

    async def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        contents = game_messages.game_update_for_declaration(self, self.players[player], declaration)
        await self.network_delegate.broadcast_message(player, contents)

    def setup_state(self):
        self.state = state_methods.create_default_state(tuple(self.players.keys()))

        for (name, player) in self.players.items():
            cards = player.get_cards()
            self.state = state_methods.update_state_upon_receiving_cards(self.state, name, cards)

    def get_player_names(self):
        return list(self.players.keys())

    def get_player_cards(self, player: str) -> tuple:
        return state_methods.get_cards_for_player(self.state, player)

    def get_player_card_count(self, player: str) -> int:
        return len(self.get_player_cards(player))

    def get_team_for_player(self, player: str) -> str:
        for (team_name, players) in self.teams.items():
            if player in players:
                return team_name

        raise Exception('Could not find team for player {0}'.format(player))

    def get_opposing_team_for_player(self, player: str) -> str:
        for (team_name, players) in self.teams.items():
            if player not in players:
                return team_name

    # PRIVATE METHODS

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.players[player_name].has_card(card)
