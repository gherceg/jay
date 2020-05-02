from typing import List
import logging

from app.constants import *
from app.data.game_data import Player, Game
from app.data.turn_data import Question, Declaration
from app.util import Optional
from app import game_state_updates

logger = logging.getLogger(__name__)


def handle_question(game: Game, questioner: str, respondent: str, card: str) -> Game:
    """Determines question outcome, updates game, requests to send up via delegate"""
    game = update_game_for_question(game, questioner, respondent, card)
    return game
    # await self.send_game_update()
    #
    # player_up_next = self.get_player_up_next()
    # while player_up_next.is_present() and player_up_next.get().player_type == COMPUTER_PLAYER:
    #     await self.automate_turn(player_up_next.get())
    #     player_up_next = self.get_player_up_next()


# async def automate_turn(self, player: Player):
#     await asyncio.sleep(COMPUTER_WAIT_TIME)
#     generated_turn: dict = cpm.generate_turn(player, self.get_opponents_names_in_play(player))
#     error = message_validation.validate_question(self.game, generated_turn)
#     if error.is_present() and generated_turn[TURN_TYPE] != DECLARATION:
#         logger.error(
#             f'Computer {player.name} is asking invalid question: {error.get()}\nHas {player.get_cards()}\n{player.state}')
#
#     self.verify_cards_left_makes_sense()
#
#     if generated_turn[TURN_TYPE] != QUESTION and generated_turn[TURN_TYPE] != DECLARATION:
#         raise Exception(f'Generated turn of type {generated_turn[TURN_TYPE]}')
#
#     if generated_turn[TURN_TYPE] == QUESTION:
#         self.update_game_for_question(generated_turn[QUESTIONER], generated_turn[RESPONDENT],
#                                       generated_turn[CARD])
#     else:
#         self.update_game_for_declaration(generated_turn[NAME],
#                                          generated_turn[CARD_SET],
#                                          generated_turn[DECLARED_MAP])
#     await self.send_game_update()


def update_game_for_question(game: Game, questioner: str, respondent: str, card: str) -> Game:
    player_asking: Player = game.players[questioner]
    player_answering: Player = game.players[respondent]

    outcome = card in player_answering.get_cards()
    logger.info(
        f'QUESTION: {questioner} asking {respondent} for the {card}. Outcome is {outcome}')
    game.player_up_next = Optional(questioner) if outcome else Optional(respondent)
    question = Question(questioner, respondent, card, outcome)
    game.ledger.append(question)
    update_state_for_question(game, question)
    return game


def update_state_for_question(game: Game, question: Question):
    # update game's state
    game.state = game_state_updates.update_state_with_turn(game.state, question)

    players_out = game_state_updates.get_players_out_of_cards(game.state)
    for key, player in game.players.items():
        player.state = game_state_updates.update_player_state_for_question(player.state, question, players_out)
