import logging
import json
from starlette.websockets import WebSocket
from typing import Dict
import asyncio

from app.network.NetworkDelegate import NetworkDelegate
from app.game.GameFactory import GameFactory
from app.game.Game import Game
from app.Constants import *
from app.util.UtilMethods import *

logger = logging.getLogger(__name__)


class Server(NetworkDelegate):
    """Inspects incoming messages to determine which game to update, and sends messages back to clients"""

    def __init__(self):
        self.connections: list = []
        self.clients: dict = {}
        self.game = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        logger.info('Connected new client {0}'.format(websocket.client))
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        logger.info('Disconnecting client {0}'.format(websocket.client))
        self.connections.remove(websocket)

    async def handle_message(self, websocket: WebSocket, message: str):
        optional_message = self.parse(message)
        if optional_message.is_empty():
            await self.send_error(websocket, 'Cannot parse message: Received unexpected format.')

        message = optional_message.value

        logger.debug('Received message from client: {0}'.format(message))

        if MESSAGE_TYPE not in message:
            await self.send_error(websocket, 'Cannot parse message: Missing message_type field')

        if DATA not in message:
            await self.send_error(websocket, 'Cannot parse message: Missing data field')

        data = message[DATA]

        if message[MESSAGE_TYPE] == CREATE_GAME:
            await self.handle_create_game_request(websocket, data)

        elif message[MESSAGE_TYPE] == ENTER_PIN:
            await self.handle_enter_pin_request(websocket, data)

        elif message[MESSAGE_TYPE] == SELECT_PLAYER:
            await self.handle_select_player_request(websocket, data)

        elif message[MESSAGE_TYPE] == QUESTION:
            if IDENTIFIER in data and data[IDENTIFIER] in self.clients.keys():
                await self.handle_question(websocket, data)
            else:
                logger.error('Server.py: QUESTION missing client id. Closing connection.')
                await websocket.close()

        elif message[MESSAGE_TYPE] == DECLARATION:
            if IDENTIFIER in data and data[IDENTIFIER] in self.clients.keys():
                await self.handle_declaration(websocket, data)
            else:
                logger.error('Server.py: DECLARATION missing client id. Closing connection.')
                await websocket.close()

        elif message[MESSAGE_TYPE] == HANDSHAKE:
            logger.info('Connecting New Client')

    async def handle_create_game_request(self, websocket: WebSocket, data: dict):
        if self.game:
            logger.info('Deleting Existing Game')
            self.game = None

        self.game = GameFactory.create_game(self, data)
        logger.info('Create Game Request: created new game with pin {0}'.format(self.game.pin))

        data_to_send = {
            MESSAGE_TYPE: CREATED_GAME,
            DATA: {
                PIN: self.game.pin,
            }
        }
        await self.send_message(websocket, data_to_send)

    async def handle_enter_pin_request(self, websocket: WebSocket, data: dict):
        if PIN in data:
            if self.game and data[PIN] == self.game.pin:
                data_to_send = {
                    MESSAGE_TYPE: JOINED_GAME,
                    DATA: {
                        TEAMS_KEY: self.game.get_teams_json(),
                        NEXT_TURN: self.game.up_next
                    }
                }
                await self.send_message(websocket, data_to_send)
            else:
                await self.send_error(websocket, 'Enter Pin Request: Invalid pin')
        else:
            await self.send_error(websocket, 'Enter Pin Request: Missing pin field')

    async def handle_select_player_request(self, websocket: WebSocket, data: dict):
        # check to make sure the expected fields exist
        if NAME in data:
            client_id = self.register_new_client(data[NAME], websocket)
            if self.game.virtual_deck is False:
                if CARDS in data:
                    self.game.players[data[NAME]].set_initial_cards(data[CARDS])
                else:
                    await self.send_error(websocket, 'Select Player Request: Missing cards field')

            data_to_send = {
                MESSAGE_TYPE: SELECTED_PLAYER,
                DATA: {
                    IDENTIFIER: client_id,
                    NAME: data[NAME],
                    CARDS: self.game.players[data[NAME]].get_cards(),
                }
            }
            await self.send_message(websocket, data_to_send)
        else:
            await self.send_error('Select Player Request: Missing name field')

    async def handle_question(self, websocket: WebSocket, data: dict):
        logger.info('Received question')
        if QUESTIONER in data and RESPONDENT in data and CARD in data:
            await self.game.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])
        else:
            await self.send_error(websocket, 'Question Request: Missing questioner, respondent or card field')

    async def handle_declaration(self, websocket: WebSocket, data: dict):
        logger.info('Received declaration')
        card_set = card_set_for_key(data[CARD_SET])
        if PLAYER_KEY in data and CARD_SET in data and DECLARED_MAP in data and card_set.is_present():
            self.game.handle_declaration(data[PLAYER_KEY], data[CARD_SET], data[DECLARED_MAP])
        else:
            await self.send_error(websocket, 'Declaration Request: Missing player, card_set or declared_map field')

    def register_new_client(self, identifier: str, websocket: WebSocket) -> str:
        logger.info('Registering new client with id: {0}'.format(identifier))
        self.clients[identifier] = websocket
        return identifier

    @staticmethod
    async def send_error(websocket: WebSocket, message: str):
        logger.error(message)
        data = {
            MESSAGE_TYPE: ERROR,
            DATA: {
                DESCRIPTION: message
            }
        }
        await websocket.send_json(data)

    @staticmethod
    async def send_message(websocket: WebSocket, data: Dict):
        logger.info('Sending message to websocket {0}: {1}'.format(websocket.client, data))
        await websocket.send_json(data)

    @staticmethod
    def parse(message) -> Optional:
        if isinstance(message, str):
            return Optional(json.loads(message))
        elif isinstance(message, dict):
            return Optional(message)
            # return json.dumps(message)

        return Optional.empty()

    # Network Delegate Implementation
    async def broadcast_message(self, name: str, contents: Dict):
        # message = self.parse(contents)
        # QS: maybe change from client_id to user name? Where do we want
        # to keep another list of user names to unique client ids. These
        # client IDs will need to be different than the websocket IDs, I think.
        # TODO: come back to figure out how to register clients
        logger.debug('Client keys: {0}'.format(self.clients.keys()))
        if name in self.clients.keys():
            websocket = self.clients[name]
            await websocket.send_json(contents)
        else:
            logger.warning('Could not find {0} in client dict'.format(name))
