from app.game.data import Turn, Declaration, CardSet
from app.player import TurnDelegate, QuestionDelegate
from app.network import NetworkDelegate
from app.constants import *
from app.util import Optional
from app.game import game_messages


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
            self.teams[team[NAME]] = team[PLAYERS]

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

    # TurnDelegate Methods
    async def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        contents = game_messages.game_update(self, self.players[player], Optional(turn))
        await self.network_delegate.broadcast_message(player, contents)

    async def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        contents = game_messages.game_update_for_declaration(self, self.players[player], declaration)
        await self.network_delegate.broadcast_message(player, contents)

    def get_player_names(self):
        return list(self.players.keys())

    # PRIVATE METHODS

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.players[player_name].has_card(card)