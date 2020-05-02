import logging
from pandas import DataFrame
import random
import asyncio
from typing import Dict, List

from app.data.game_enums import CardSet
from app.data.game_data import Game, Player, Team
from app.data.turn_data import Declaration, Question
from app.data.network_data import NetworkDelegate
from app.constants import *
from app.util import Optional
from app import message_builder, message_validation, game_state_updates, computer_player as cpm, network_methods

logger = logging.getLogger(__name__)


class GameManager:
    """Responsible for managing a game and its players"""

    def __init__(self, network_delegate: NetworkDelegate, game: Game):
        self.network_delegate = network_delegate
        self.game = game

    async def handle_declaration(self, player: str, card_set: CardSet, declared_list: list):
        """Determines declaration outcome, updates game, requests to send up via delegate"""
        self.update_game_for_declaration(player, card_set, tuple(declared_list))
        await self.send_game_update()

        if self.game.player_up_next.is_empty():
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

    async def automate_turn(self, player: Player):
        await asyncio.sleep(COMPUTER_WAIT_TIME)
        generated_turn: dict = cpm.generate_turn(player, self.get_opponents_names_in_play(player))
        error = message_validation.validate_question(self.game, generated_turn)
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
        self.game.player_up_next = Optional(questioner) if outcome else Optional(respondent)
        question = Question(questioner, respondent, card, outcome)
        self.game.ledger.append(question)
        self.update_state_for_question(question)

    def update_game_for_declaration(self, player_name: str, card_set: CardSet, declared_list: tuple):
        outcome = True
        for card_player_pair in declared_list:
            outcome = self.does_player_have_card(card_player_pair[PLAYER], card_player_pair[CARD]) and outcome
        logger.info(
            f'DECLARATION: {player_name} declared the {card_set}. Outcome is {outcome}\n{declared_list}')

        # TODO not the most elegant way to do this
        player_who_declared = self.game.players[player_name]
        team_name = player_who_declared.team_name if outcome else self.get_opposing_team_name_for_player(player_name)
        self.game.teams[team_name].sets_won += 1

        declaration: Declaration = Declaration(player_name, card_set, declared_list, outcome)
        self.game.ledger.append(declaration)

        self.update_state_for_declaration(declaration)

        self.game.player_up_next = self.determine_player_up_next_after_declaration(player_who_declared, outcome)
        if self.game.player_up_next.is_present():
            logger.info(f'{self.game.player_up_next.get()} is up next')

    def update_state_for_declaration(self, declaration: Declaration):
        # update game's state
        self.game.state = game_state_updates.update_state_with_declaration(self.game.state, declaration)

        players_out = game_state_updates.get_players_out_of_cards(self.game.state)
        for key, player in self.game.players.items():
            player.state = game_state_updates.update_player_state_for_declaration(player.state, declaration, players_out)

    def update_state_for_question(self, question: Question):
        # update game's state
        self.game.state = game_state_updates.update_state_with_turn(self.game.state, question)

        players_out = game_state_updates.get_players_out_of_cards(self.game.state)
        for key, player in self.game.players.items():
            player.state = game_state_updates.update_player_state_for_question(player.state, question, players_out)

    async def send_game_update(self):
        logger.info(f'Sending game update to all clients')
        for key, player in self.game.players.items():
            if player.player_type == NETWORK_PLAYER:
                await self.broadcast_turn(player)

    async def send_end_game(self):
        for key, player in self.game.players.items():
            if player.player_type == NETWORK_PLAYER:
                await self.broadcast_end_game(player.name)

    # Network Methods
    async def broadcast_turn(self, player: Player):
        contents = message_builder.game_update(self.game, player)
        client_identifier = network_methods.client_identifier(player.name, str(self.game.pin))
        await self.network_delegate.broadcast_message(client_identifier, contents)

    async def broadcast_end_game(self, name: str):
        contents = message_builder.end_game(self.game)
        client_identifier = network_methods.client_identifier(name, str(self.game.pin))
        await self.network_delegate.broadcast_message(client_identifier, contents)

    # Set Methods
    def set_player_to_start(self, player: str):
        self.game.player_up_next = Optional(player)
        # TODO: if computer, let them know

    # Get Methods
    def get_player_up_next(self) -> Optional[Player]:
        if self.game.player_up_next.is_present():
            player = self.game.players[self.game.player_up_next.get()]
            return Optional(player)
        else:
            return Optional.empty()

    def get_player_names(self):
        return list(self.game.players.keys())

    def get_player_cards(self, player: str) -> List[str]:
        return game_state_updates.get_cards_for_player(self.game.state, player)

    def get_player_type(self, player: str) -> str:
        return self.game.players[player].player_type

    def get_player_card_count(self, player: str) -> int:
        return len(self.get_player_cards(player))

    def get_team_name_for_player(self, player: str) -> str:
        for team in self.game.teams.values():
            if player in team.player_names:
                return team.name

        raise Exception('Could not find team for player {0}'.format(player))

    # TODO could refactor
    def get_opposing_team_name_for_player(self, player: str) -> str:
        for team in self.game.teams.values():
            if player not in team.player_names:
                return team.name

    def get_opponents_names_in_play(self, player: Player) -> List[str]:
        eligible_players = []
        for temp_player in self.game.players.values():
            if temp_player.team_name != player.team_name and temp_player.in_play:
                eligible_players.append(temp_player.name)

        return eligible_players

    def get_opponents_in_play(self, player: Player) -> List[Player]:
        eligible_players = []
        for temp_player in self.game.players.values():
            if temp_player.team_name != player.team_name and temp_player.in_play:
                eligible_players.append(temp_player)

        return eligible_players

    def get_teammates_in_play(self, player: Player) -> List[Player]:
        eligible_players = []
        for temp_player in self.game.players.values():
            logger.info(f'Finding eligible teammates: {temp_player.name} on team {temp_player.team_name}')
            if temp_player.team_name == player.team_name and temp_player.in_play:
                eligible_players.append(temp_player)

        return eligible_players

    # PRIVATE METHODS

    def determine_player_up_next_after_declaration(self, player: Player, outcome: bool) -> Optional[str]:
        eligible_opponents = self.get_opponents_in_play(player)
        eligible_teammates = self.get_teammates_in_play(player)
        eligible_teammate_names = map(lambda p: p.name, eligible_teammates)
        eligible_opponent_names = map(lambda p: p.name, eligible_opponents)

        logger.info(
            f'Determining player up next after {"successful" if outcome else "failed"} declaration\nPlayer in play: {player.in_play}\nEligible teammates: {list(eligible_teammate_names)}\nEligible opponents: {list(eligible_opponent_names)}')
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
                opponent = random.choice(eligible_opponents)
                return Optional(opponent.name)
            elif player.in_play:
                return Optional(player.name)
            elif len(eligible_teammates) > 0:
                teammate = random.choice(eligible_teammates)
                return Optional(teammate.name)
            elif self.game_is_over():
                return Optional.empty()
            else:
                raise Exception('Everyone is out but the game is not over.')

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.game.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.game.players[player_name].has_card(card)

    def game_is_over(self) -> bool:
        total_sets_won = 0
        for team in self.game.teams.values():
            total_sets_won += team.sets_won

        logger.info(f'Total sets won: {total_sets_won}')
        return total_sets_won == 8

    # DEBBUG Method
    def verify_cards_left_makes_sense(self):
        card_count = 0
        for player in self.game.players.values():
            card_count += len(player.get_cards())

        sets_declared = 0
        for team in self.game.teams.values():
            sets_declared += team.sets_won
        expected_card_count = 48 - (sets_declared * 6)

        if card_count != expected_card_count:
            logger.error('Card Count Mismatch!')
