import logging
from starlette.websockets import WebSocket, WebSocketState
from typing import Dict

from app import message_builder, message_handling
from app.data import Client
from app.game import GameManager
from app.constants import *
from app.network import NetworkDelegate, network_methods

logger = logging.getLogger(__name__)


class Server(NetworkDelegate):
    """Inspects incoming messages to determine which game to update, and sends messages back to clients"""

    def __init__(self):
        # use client to identify player and game they are apart of
        self.clients: Dict[str, Client] = {}

        # hold onto game references
        # TODO persist games
        self.game_managers: Dict[int, GameManager] = {}

    def remove(self, websocket: WebSocket):
        websocket_identifier = network_methods.websocket_identifier(websocket)
        for client in self.clients.values():
            if websocket_identifier in client.connections.keys():
                # remove only the connection from client
                del client.connections[websocket_identifier]

    async def handle_message(self, websocket: WebSocket, message: dict):

        if MESSAGE_TYPE not in message:
            await network_methods.send_error(websocket, 'Cannot parse message: Missing message_type field')

        if DATA not in message:
            await network_methods.send_error(websocket, 'Cannot parse message: Missing data field')

        data = message[DATA]

        if message[MESSAGE_TYPE] == CREATE_GAME:
            game_manager = await message_handling.handle_create_game_request(self, websocket, data)
            self.game_managers[game_manager.game.pin] = game_manager

        elif message[MESSAGE_TYPE] == ENTER_PIN:
            if PIN in data and data[PIN] in self.game_managers.keys():
                game_manager: GameManager = self.game_managers[data[PIN]]
                await message_handling.handle_enter_pin_request(websocket, game_manager.game)
            else:
                await network_methods.send_error('Enter Pin Request: Missing or invalid pin field')

        elif message[MESSAGE_TYPE] == SELECT_PLAYER:
            if PIN in data and data[PIN] in self.game_managers.keys():
                game_manager: GameManager = self.game_managers[data[PIN]]
                if NAME in data:
                    self.register_client(data[NAME], data[PIN], websocket)
                    await message_handling.handle_select_player_request(websocket, game_manager.game, data)
            else:
                await network_methods.send_error('Select Player Request: Missing or invalid pin field')

        elif message[MESSAGE_TYPE] == QUESTION:
            if PIN in data and data[PIN] in self.game_managers.keys():
                game_manager: GameManager = self.game_managers[data[PIN]]
                await message_handling.handle_question(websocket, game_manager, data)
            else:
                await network_methods.send_error('Enter Question: Missing or invalid pin field')

        elif message[MESSAGE_TYPE] == DECLARATION:
            if PIN in data and data[PIN] in self.game_managers.keys():
                game_manager: GameManager = self.game_managers[data[PIN]]
                await message_handling.handle_declaration(websocket, game_manager, data)
            else:
                await network_methods.send_error('Enter Question: Missing or invalid pin field')

    def register_client(self, player_id: str, game_id: str, websocket: WebSocket):
        # check if client exists
        client_identifier = network_methods.client_identifier(player_id, game_id)
        websocket_identifier = network_methods.websocket_identifier(websocket)
        if client_identifier in self.clients.keys():
            # client already exists, add connection to dictionary
            client = self.clients[client_identifier]
            self.clients[client_identifier].connections[websocket_identifier] = websocket
            logger.info(f'Registered new connection with client\n{client}')
        else:
            # setup client
            client = Client(game_id, player_id)
            client.connections[websocket_identifier] = websocket
            self.clients[client.identifier] = client
            logger.info(f'Registered new client\n{client}')

    # Network Delegate Implementation
    async def broadcast_message(self, client_id: str, contents: Dict):
        if client_id not in self.clients.keys():
            logger.warning(f'Could not find client for identifier {client_id}')
            return

        client = self.clients[client_id]
        for identifier, websocket in client.connections.items():
            try:
                logger.info(f'Sending message to client {client.identifier} connection {identifier}')
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.send_json(contents)
                else:
                    logger.error(f'Websocket {identifier} is disconnected. Not sending message')
            except:
                # TODO figure out concurrency issue with not receiving disconnect until event loop is idle again
                #  to avoid broad exception clause, figure out a specific exception to catch.
                #  The crash is due to starlette.websockets.exceptions.ConnectionClosedOK
                logger.error('Attempted to send message to disconnected websocket.')
