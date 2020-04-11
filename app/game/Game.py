import logging
from pandas import DataFrame
import random
import asyncio

from app.game.data import Turn, Declaration, CardSet
from app.player import PlayerInterface, state_methods, computer_player_methods as cpm
from app.network import NetworkDelegate
from app.constants import *
from app.util import Optional
from app.game import game_messages, game_validation

logger = logging.getLogger(__name__)


class Game:
    """Responsible for managing a game and its players"""

    def __init__(self, pin: int, network_delegate: NetworkDelegate, players: tuple, teams: tuple, virtual_deck: bool):
        self.network_delegate = network_delegate
        self.pin: int = pin
        self.ledger: list = []
        self.up_next: Optional[str] = Optional.empty()
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

    async def handle_declaration(self, player: str, card_set: CardSet, declared_list: list):
        """Determines declaration outcome, updates game, requests to send up via delegate"""
        self.update_game_for_declaration(player, card_set, tuple(declared_list))
        logger.info(self.state)
        await self.send_game_update()

        if self.up_next.is_empty():
            logger.info('Sending end game messages!')
            await self.send_end_game()
            return

        player_up_next = self.get_player_up_next()
        while player_up_next.is_present() and player_up_next.get().player_type == COMPUTER_PLAYER:
            await self.automate_turn(player_up_next.get())
            player_up_next = self.get_player_up_next()

    async def handle_question(self, questioner: str, respondent: str, card: str):
        """Determines question outcome, updates game, requests to send up via delegate"""
        self.update_game_for_question(questioner, respondent, card)
        await self.send_game_update()

        player_up_next = self.get_player_up_next()
        while player_up_next.is_present() and player_up_next.get().player_type == COMPUTER_PLAYER:
            await self.automate_turn(player_up_next.get())
            player_up_next = self.get_player_up_next()

    async def automate_turn(self, player: PlayerInterface):
        await asyncio.sleep(COMPUTER_WAIT_TIME)
        generated_turn: dict = cpm.generate_turn(player, self.get_opponents_names_in_play(player))
        error = game_validation.validate_question(self, generated_turn)
        if error.is_present() and generated_turn[TURN_TYPE] != DECLARATION:
            logger.error(
                f'Computer {player.name} is asking invalid question: {error.get()}\nHas {player.get_cards()}\n{player.state}')

        self.verify_cards_left_makes_sense()

        if generated_turn[TURN_TYPE] != QUESTION and generated_turn[TURN_TYPE] != DECLARATION:
            raise Exception(f'Generated turn of type {generated_turn[TURN_TYPE]}')

        if generated_turn[TURN_TYPE] == QUESTION:
            self.update_game_for_question(generated_turn[QUESTIONER], generated_turn[RESPONDENT],
                                          generated_turn[CARD])
        else:
            self.update_game_for_declaration(generated_turn[NAME],
                                             generated_turn[CARD_SET],
                                             generated_turn[DECLARED_MAP])
        await self.send_game_update()

    def update_game_for_question(self, questioner: str, respondent: str, card: str):
        outcome = self.does_player_have_card(respondent, card)
        logger.info(
            f'QUESTION: {questioner} asking {respondent} for the {card}. Outcome is {outcome}')
        self.up_next = Optional(questioner) if outcome else Optional(respondent)
        turn = Turn(questioner, respondent, card, outcome)
        self.ledger.append(turn)
        self.update_state_for_question(turn)

    def update_game_for_declaration(self, player_name: str, card_set: CardSet, declared_list: tuple):
        outcome = True
        for card_player_pair in declared_list:
            outcome = self.does_player_have_card(card_player_pair[PLAYER], card_player_pair[CARD]) and outcome
        logger.info(
            f'DECLARATION: {player_name} declared the {card_set}. Outcome is {outcome}\n{declared_list}')

        # TODO not the most elegant way to do this
        player_who_declared = self.players[player_name]
        team_name = player_who_declared.team_name if outcome else self.get_opposing_team_name_for_player(player_name)
        self.set_counts[team_name] += 1

        declaration: Declaration = Declaration(player_name, card_set, declared_list, outcome)
        self.ledger.append(declaration)

        self.update_state_for_declaration(declaration)

        self.up_next = self.determine_player_up_next_after_declaration(player_who_declared, outcome)

    def update_state_for_declaration(self, declaration: Declaration):
        # update game's state
        self.state = state_methods.update_state_with_declaration(self.state, declaration)

        players_out = state_methods.get_players_out_of_cards(self.state)
        for key, player in self.players.items():
            player.received_declaration(declaration, players_out)

    def update_state_for_question(self, question: Turn):
        # update game's state
        self.state = state_methods.update_state_with_turn(self.state, question)

        players_out = state_methods.get_players_out_of_cards(self.state)
        for key, player in self.players.items():
            player.received_next_turn(question, players_out)

    async def send_game_update(self):
        for key, player in self.players.items():
            if player.player_type == NETWORK_PLAYER:
                await self.broadcast_turn(player)

    async def send_end_game(self):
        for key, player in self.players.items():
            if player.player_type == NETWORK_PLAYER:
                await self.broadcast_end_game()

    # Network Methods
    async def broadcast_turn(self, player: PlayerInterface):
        contents = game_messages.game_update(self, player)
        await self.network_delegate.broadcast_message(player.name, contents)

    async def broadcast_end_game(self):
        contents = game_messages.end_game(self)
        await self.network_delegate.broadcast_message(contents)

    # Set Methods
    def set_player_to_start(self, player: str):
        self.up_next = Optional(player)
        # TODO: if computer, let them know

    # Get Methods
    def get_player_up_next(self) -> Optional[PlayerInterface]:
        if self.up_next.is_present():
            player = self.players[self.up_next.get()]
            return Optional(player)
        else:
            return Optional.empty()

    def get_player_names(self):
        return list(self.players.keys())

    def get_player_cards(self, player: str) -> tuple:
        return state_methods.get_cards_for_player(self.state, player)

    def get_player_type(self, player: str) -> str:
        return self.players[player].player_type

    def get_player_card_count(self, player: str) -> int:
        return len(self.get_player_cards(player))

    def get_team_name_for_player(self, player: str) -> str:
        for (team_name, players) in self.teams.items():
            if player in players:
                return team_name

        raise Exception('Could not find team for player {0}'.format(player))

    # TODO could refactor
    def get_opposing_team_name_for_player(self, player: str) -> str:
        for (team_name, players) in self.teams.items():
            if player not in players:
                return team_name

    def get_opponents_names_in_play(self, player: PlayerInterface) -> tuple:
        eligible_players = []
        for temp_player in self.players.values():
            if temp_player.team_name != player.team_name and temp_player.in_play:
                eligible_players.append(temp_player.name)

        return tuple(eligible_players)

    def get_opponents_in_play(self, player: PlayerInterface) -> tuple:
        eligible_players = []
        for temp_player in self.players.values():
            if temp_player.team_name != player.team_name and temp_player.in_play:
                eligible_players.append(temp_player)

        return tuple(eligible_players)

    def get_teammates_in_play(self, player: PlayerInterface) -> tuple:
        eligible_players = []
        for temp_player in self.players.values():
            if temp_player.team_name != player.team_name and temp_player.in_play:
                eligible_players.append(temp_player)

        return tuple(eligible_players)

    # PRIVATE METHODS

    def setup_state(self):
        self.state = state_methods.create_default_state(tuple(self.players.keys()))

        for (name, player) in self.players.items():
            cards = player.get_cards()
            self.state = state_methods.update_state_upon_receiving_cards(self.state, name, cards)

    def determine_player_up_next_after_declaration(self, player: PlayerInterface, outcome: bool) -> Optional[str]:
        eligible_opponents = self.get_opponents_in_play(player)
        eligible_teammates = self.get_teammates_in_play(player)

        if outcome:
            if player.in_play:
                return Optional(player.name)
            elif len(eligible_teammates) > 0:
                teammate = random.choice(eligible_teammates)
                return Optional(teammate.name)
            elif len(eligible_opponents) > 0:
                opponent = random.choice(eligible_opponents)
                return Optional(opponent.name)
            elif self.game_is_over():
                return Optional.empty()
            else:
                raise Exception('Everyone is out but the game is not over.')
        else:
            if len(eligible_opponents) > 0:
                opponent = random.choice(eligible_teammates)
                return Optional(opponent.name)
            elif player.in_play:
                return Optional(player.name)
            elif len(eligible_teammates) > 0:
                teammate = random.choice(eligible_opponents)
                return Optional(teammate.name)
            elif self.game_is_over():
                return Optional.empty()
            else:
                raise Exception('Everyone is out but the game is not over.')

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.players[player_name].has_card(card)

    def game_is_over(self) -> bool:
        total_sets_won = 0
        for set_count in self.set_counts.values():
            total_sets_won += set_count

        logger.info(f'Total sets won: {total_sets_won}')
        return total_sets_won == 8

    # DEBBUG Method
    def verify_cards_left_makes_sense(self):
        card_count = 0
        for player in self.players.values():
            card_count += len(player.get_cards())

        sets_declared = 0
        for set_count in self.set_counts.values():
            sets_declared += set_count
        expected_card_count = 48 - (sets_declared * 6)

        if card_count != expected_card_count:
            logger.error('Card Count Mismatch!')
