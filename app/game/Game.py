import logging
from pandas import DataFrame
import random
import asyncio

from app.game.data import Turn, Declaration, CardSet
from app.player import PlayerInterface, state_methods, computer_player_methods as cpm
from app.network import NetworkDelegate
from app.constants import *
from app.util import Optional
from app.game import game_messages

logger = logging.getLogger(__name__)


class Game:
    """Responsible for managing a game and its players"""

    def __init__(self, pin: int, network_delegate: NetworkDelegate, players: tuple, teams: tuple, virtual_deck: bool):
        self.network_delegate = network_delegate
        self.pin: int = pin
        self.ledger: list = []
        self.up_next: str = None
        self.state: DataFrame = None
        self.virtual_deck: bool = virtual_deck

        # create a dictionary of players for easy lookup
        self.players: dict = {}
        for player in players:
            self.players[player.name] = player

        self.teams = {}
        for team in teams:
            self.teams[team[NAME]] = team[PLAYERS]
            # TODO refactor teams to associate team name with player better
            for player in team[PLAYERS]:
                player: PlayerInterface = self.players[player]
                player.team_name = team[NAME]

        self.set_counts = {}
        for team in teams:
            self.set_counts[team[NAME]] = 0

        self.setup_state()

    def setup_state(self):
        self.state = state_methods.create_default_state(tuple(self.players.keys()))

        for (name, player) in self.players.items():
            cards = player.get_cards()
            self.state = state_methods.update_state_upon_receiving_cards(self.state, name, cards)

    async def handle_declaration(self, player: str, card_set: CardSet, declared_list: list):
        declaration: Declaration = self.update_game_for_declaration(player, card_set, tuple(declared_list))
        await self.send_declaration_update(declaration)

        player_up_next = self.players[self.up_next]
        while player_up_next.player_type == COMPUTER_PLAYER:
            await self.automate_turn(player_up_next)
            player_up_next = self.players[self.up_next]
            await asyncio.sleep(COMPUTER_WAIT_TIME)

    async def handle_question(self, questioner: str, respondent: str, card: str):
        turn: Turn = self.update_game_for_question(questioner, respondent, card)
        await self.send_question_update(turn)

        player_up_next = self.players[self.up_next]
        while player_up_next.player_type == COMPUTER_PLAYER:
            await self.automate_turn(player_up_next)
            player_up_next = self.players[self.up_next]
            await asyncio.sleep(COMPUTER_WAIT_TIME)

    async def automate_turn(self, player: PlayerInterface):
        generated_turn: dict = cpm.generate_turn(player, self.get_eligible_player_names_to_ask(player))
        if generated_turn[TURN_TYPE] == QUESTION:
            turn: Turn = self.update_game_for_question(generated_turn[QUESTIONER], generated_turn[RESPONDENT],
                                                       generated_turn[CARD])
            await self.send_question_update(turn)
        elif generated_turn[TURN_TYPE] == DECLARATION:
            declaration: Declaration = self.update_game_for_declaration(generated_turn[NAME],
                                                                        generated_turn[CARD_SET],
                                                                        generated_turn[DECLARED_MAP])
            await self.send_declaration_update(declaration)
        else:
            logging.error(f'Returned dictionary turn type value is {generated_turn[TURN_TYPE]}')

    def update_game_for_question(self, questioner: str, respondent: str, card: str) -> Turn:
        outcome = self.does_player_have_card(respondent, card)
        logger.info(
            f'Updating game for question: {questioner} asking {respondent} for the {card}. Outcome is {outcome}')
        self.up_next = questioner if outcome else respondent
        turn = Turn(questioner, respondent, card, outcome)
        self.state = state_methods.update_state_with_turn(self.state, turn)
        self.ledger.append(turn)
        for key, player in self.players.items():
            player.received_next_turn(turn)
        return turn

    def update_game_for_declaration(self, player_name: str, card_set: CardSet, declared_list: tuple) -> Declaration:
        outcome = True
        for card_player_pair in declared_list:
            outcome = self.does_player_have_card(card_player_pair[PLAYER], card_player_pair[CARD]) and outcome

        # TODO not the most elegant way to do this
        player = self.players[player_name]
        team_name = player.team_name if outcome else self.get_opposing_team_name_for_player(player_name)
        self.set_counts[team_name] += 1

        declaration: Declaration = Declaration(player_name, card_set, declared_list, outcome)

        self.state = state_methods.update_state_with_declaration(self.state, declaration)
        self.ledger.append(declaration)
        for key, player in self.players.items():
            player.received_declaration(declaration)
        return declaration

    async def send_question_update(self, turn):
        for key, player in self.players.items():
            if player.player_type == NETWORK_PLAYER:
                await self.broadcast_turn(player, turn)

    async def send_declaration_update(self, declaration: Declaration):
        for key, player in self.players.items():
            if player.player_type == NETWORK_PLAYER:
                await self.broadcast_declaration(player, declaration)

    # Network Methods
    async def broadcast_turn(self, player: PlayerInterface, turn: Turn):
        contents = game_messages.game_update(self, player, Optional(turn))
        await self.network_delegate.broadcast_message(player.name, contents)

    async def broadcast_declaration(self, player: PlayerInterface, declaration: Declaration):
        contents = game_messages.game_update_for_declaration(self, player, declaration)
        await self.network_delegate.broadcast_message(player.name, contents)

    # Set Methods
    def set_player_to_start(self, player: str):
        self.up_next = player
        # TODO: if computer, let them know

    # Get Methods
    def get_player_names(self):
        return list(self.players.keys())

    def get_player_cards(self, player: str) -> tuple:
        return state_methods.get_cards_for_player(self.state, player)

    def get_player_card_count(self, player: str) -> int:
        return len(self.get_player_cards(player))

    def get_team_name_for_player(self, player: str) -> str:
        for (team_name, players) in self.teams.items():
            if player in players:
                return team_name

        raise Exception('Could not find team for player {0}'.format(player))

    #TODO could refactor
    def get_opposing_team_name_for_player(self, player: str) -> str:
        for (team_name, players) in self.teams.items():
            if player not in players:
                return team_name

    def get_eligible_player_names_to_ask(self, player: PlayerInterface) -> tuple:
        eligible_players = []
        for temp_player in self.players.values():
            if temp_player.team_name != player.team_name and temp_player.in_play:
                eligible_players.append(temp_player.name)

        return tuple(eligible_players)

    # PRIVATE METHODS

    def determine_player_up_next(self, player: str, outcome: bool) -> str:
        # TODO: should keep track of those still in play
        pass

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.players[player_name].has_card(card)
