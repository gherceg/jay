import logging
from starlette.websockets import WebSocket, WebSocketState
from typing import Dict

from app.game import Game, game_messages, game_builder, game_validation
from app.util import util_methods
from app.constants import *
from app.network import Client, NetworkDelegate, network_methods

logger = logging.getLogger(__name__)


class Server(NetworkDelegate):
    """Inspects incoming messages to determine which game to update, and sends messages back to clients"""

    def __init__(self):
        self.clients: Dict[str, Client] = {}
        # TODO change pin to string
        self.games: Dict[int, Game] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    def remove(self, websocket: WebSocket):
        websocket_identifier = network_methods.websocket_identifier(websocket)
        for client in self.clients.values():
            if websocket_identifier in client.connections.keys():
                del client.connections[websocket_identifier]

    async def handle_message(self, websocket: WebSocket, message: dict):

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
        created_game = game_builder.create_game(self, data)
        logger.info(f'Created new game {created_game.pin}')
        self.games[created_game.pin] = created_game
        data_to_send = game_messages.created_game(created_game)
        await network_methods.send_message(websocket, data_to_send)

    async def handle_enter_pin_request(self, websocket: WebSocket, data: dict):
        if PIN in data:
            if data[PIN] in self.games.keys():
                game = self.games[data[PIN]]
                data_to_send = game_messages.joined_game(game)
                await network_methods.send_message(websocket, data_to_send)
            else:
                await network_methods.send_error(websocket, 'Enter Pin Request: Invalid pin')
        else:
            await network_methods.send_error(websocket, 'Enter Pin Request: Missing pin field')

    async def handle_select_player_request(self, websocket: WebSocket, data: dict):
        # check to make sure the expected fields exist
        if NAME in data and PIN in data and data[PIN] in self.games.keys():
            game = self.games[data[PIN]]
            self.register_client(data[NAME], data[PIN], websocket)

            # TODO do not like this, should not be grabbing reference to player
            player = game.players[data[NAME]]
            if game.virtual_deck is False:
                if CARDS in data:
                    player.set_initial_cards(data[CARDS])
                else:
                    await network_methods.send_error(websocket, 'Select Player Request: Missing cards field')

            data_to_send = game_messages.game_update(game, player)

            await network_methods.send_message(websocket, data_to_send)
        else:
            await network_methods.send_error(websocket, 'Select Player Request: Missing fields or incorrect pin')

    async def handle_question(self, websocket: WebSocket, data: dict):
        if PIN in data and data[PIN] in self.games.keys():
            game = self.games[data[PIN]]

            error = game_validation.validate_question(game, data)
            if error.is_present():
                await network_methods.send_error(websocket, error.get())
            else:
                await game.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])
        else:
            await network_methods.send_error(websocket, 'Question Request: Missing or invalid pin')

    async def handle_declaration(self, websocket: WebSocket, data: dict):
        if PIN in data and data[PIN] in self.games.keys():
            game = self.games[data[PIN]]

            card_set = util_methods.card_set_for_key(data[CARD_SET])
            if NAME in data and CARD_SET in data and DECLARED_MAP in data and card_set.is_present():
                await game.handle_declaration(data[NAME], card_set.get(), data[DECLARED_MAP])
            else:
                await network_methods.send_error(websocket,
                                                 'Declaration Request: Missing player, card_set or declared_map field')
        else:
            await network_methods.send_error(websocket, 'Declaration Request: Missing or invalid pin')

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
