from starlette.websockets import WebSocket
import logging

from app.game_manager import GameManager
from app.data.game_data import Game, Player
from app.constants import *
from app import message_validation, message_builder, game_builder, network_methods, game_updates
from app.util import util_methods
from app.data.network_data import NetworkDelegate

logger = logging.getLogger(__name__)


async def handle_create_game_request(delegate: NetworkDelegate, websocket: WebSocket, data: dict) -> GameManager:
    game = game_builder.create_game(data)
    logger.info('Create Game Request: created new game with pin {0}'.format(game.pin))
    data_to_send = message_builder.created_game(game)
    await network_methods.send_message(websocket, data_to_send)
    return GameManager(delegate, game)


async def handle_enter_pin_request(websocket: WebSocket, game: Game):
    # TODO update to only pass back selectable players (no computers, and maybe no one who already has a client)
    data_to_send = message_builder.joined_game(game)
    await network_methods.send_message(websocket, data_to_send)


async def handle_select_player_request(websocket: WebSocket, game: Game, data: dict):
    # check to make sure the expected fields exist
    if NAME in data:
        player = game.players[data[NAME]]

        if game.virtual_deck is False:
            await network_methods.send_error(websocket, 'Select Player Request: Missing cards field')

        data_to_send = message_builder.game_update(game, player)

        await network_methods.send_message(websocket, data_to_send)
    else:
        await network_methods.send_error(websocket, 'Select Player Request: Missing name field')


# TODO phase out game manager, use Game dataclass with methods to update
async def handle_question(websocket: WebSocket, game_manager: GameManager, data: dict):
    error = message_validation.validate_question(game_manager.game, data)
    if error.is_present():
        await network_methods.send_error(websocket, error.get())
    else:
        # update game for question
        await game_manager.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])


# TODO phase out game manager, use Game dataclass with methods to update
async def handle_declaration(websocket: WebSocket, game_manager: GameManager, data: dict):
    card_set = util_methods.card_set_for_key(data[CARD_SET])
    if NAME in data and CARD_SET in data and DECLARED_MAP in data and card_set.is_present():
        await game_manager.handle_declaration(data[NAME], card_set.get(), data[DECLARED_MAP])
    else:
        await network_methods.send_error(websocket,
                                         'Declaration Request: Missing player, card_set or declared_map field')
