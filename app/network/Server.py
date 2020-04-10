import logging
import json
import asyncio
from starlette.websockets import WebSocket, WebSocketDisconnect
from typing import Dict

from app.game import game_messages, game_builder, game_validation
from app.util import util_methods
from app.constants import *
from app.network import NetworkDelegate, network_methods

logger = logging.getLogger(__name__)


class Server(NetworkDelegate):
    """Inspects incoming messages to determine which game to update, and sends messages back to clients"""

    def __init__(self):
        self.connections: list = []
        self.clients: dict = {}
        self.games: dict = {}
        self.game = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        logger.info('Connected new client {0}'.format(websocket.client))
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        logger.info('Disconnecting client {0}'.format(websocket.client))
        self.connections.remove(websocket)

    async def handle_message(self, websocket: WebSocket, message: dict):

        logger.info('Received message from client: {0}'.format(message))

        if MESSAGE_TYPE not in message:
            await network_methods.send_error(websocket, 'Cannot parse message: Missing message_type field')

        if DATA not in message:
            await network_methods.send_error(websocket, 'Cannot parse message: Missing data field')

        data = message[DATA]

        if message[MESSAGE_TYPE] == CREATE_GAME:
            await self.handle_create_game_request(websocket, data)

        elif message[MESSAGE_TYPE] == ENTER_PIN:
            await self.handle_enter_pin_request(websocket, data)

        elif message[MESSAGE_TYPE] == SELECT_PLAYER:
            await self.handle_select_player_request(websocket, data)

        elif message[MESSAGE_TYPE] == QUESTION:
            await self.handle_question(websocket, data)

        elif message[MESSAGE_TYPE] == DECLARATION:
            await self.handle_declaration(websocket, data)

    async def handle_create_game_request(self, websocket: WebSocket, data: dict):
        if self.game:
            logger.info('Deleting Existing Game')
            self.game = None

        created_game = game_builder.create_game(self, data)
        self.game = created_game
        self.games[created_game.pin] = created_game
        logger.info('Create Game Request: created new game with pin {0}'.format(self.game.pin))
        data_to_send = game_messages.created_game(self.game)
        await network_methods.send_message(websocket, data_to_send)

    async def handle_enter_pin_request(self, websocket: WebSocket, data: dict):
        if PIN in data:
            if self.game and data[PIN] == self.game.pin:
                data_to_send = game_messages.joined_game(self.game)
                await network_methods.send_message(websocket, data_to_send)
            else:
                await network_methods.send_error(websocket, 'Enter Pin Request: Invalid pin')
        else:
            await network_methods.send_error(websocket, 'Enter Pin Request: Missing pin field')

    async def handle_select_player_request(self, websocket: WebSocket, data: dict):
        # check to make sure the expected fields exist
        if NAME in data:
            client_id = self.register_new_client(data[NAME], websocket)
            player = self.game.players[data[NAME]]
            if self.game.virtual_deck is False:
                if CARDS in data:
                    player.set_initial_cards(data[CARDS])
                else:
                    await network_methods.send_error(websocket, 'Select Player Request: Missing cards field')

            data_to_send = game_messages.game_update(self.game, player)

            await network_methods.send_message(websocket, data_to_send)
        else:
            await network_methods.send_error('Select Player Request: Missing name field')

    async def handle_question(self, websocket: WebSocket, data: dict):
        error = game_validation.validate_question(self.game, data)
        if error.is_present():
            await network_methods.send_error(websocket, error.get())
        else:
            await self.game.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])

    async def handle_declaration(self, websocket: WebSocket, data: dict):
        logger.info('Received declaration')
        card_set = util_methods.card_set_for_key(data[CARD_SET])
        if NAME in data and CARD_SET in data and DECLARED_MAP in data and card_set.is_present():
            await self.game.handle_declaration(data[NAME], card_set.get(), data[DECLARED_MAP])
        else:
            await network_methods.send_error(websocket,
                                             'Declaration Request: Missing player, card_set or declared_map field')

    def register_new_client(self, player_name: str, websocket: WebSocket) -> str:
        logger.info('Registering new client with id: {0}'.format(player_name))
        self.clients[player_name] = websocket
        return player_name

    # Network Delegate Implementation
    async def broadcast_message(self, name: str, contents: Dict):
        # TODO: come back to figure out how to register clients
        logger.debug('Client keys: {0}'.format(self.clients.keys()))
        if name in self.clients.keys():
            websocket = self.clients[name]
            await websocket.send_json(contents)
        else:
            logger.warning('Could not find {0} in client dict'.format(name))
