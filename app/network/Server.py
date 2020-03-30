import logging
from logging import exception
import json
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.network.NetworkDelegate import NetworkDelegate
from app.game.GameFactory import GameFactory
from app.game.Game import Game
from app.Constants import *
from app.util.UtilMethods import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Server(NetworkDelegate):
    """Holds onto websocket connections"""
    game: Game = None

    def __init__(self):
        self.connections: list = []
        self.clients: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def handle_message(self, websocket: WebSocket, message: str) -> str:
        message = self.parse(message)
        logger.debug(message)

        if MESSAGE_TYPE not in message:
            raise exception('Unknown Message Format: Server.py: No MESSAGE_TYPE field found in message.')

        if DATA not in message:
            raise exception('Unknown Message Format: Server.py: No DATA field found in message.')

        data = message[DATA]

        if message[MESSAGE_TYPE] == CREATE_GAME:
            return self.handle_create_game_request(websocket, data)

        elif message[MESSAGE_TYPE] == CONNECT_TO_GAME:
            return self.handle_connect_to_game_request(websocket, data)

        elif message[MESSAGE_TYPE] == SET_CARDS:
            if IDENTIFIER in data and data[IDENTIFIER] in self.clients.keys:
                self.handle_set_cards(data)
            else:
                logger.error('Server.py: SET_CARDS missing client id. Closing connection.')
                await websocket.close()

        elif message[MESSAGE_TYPE] == QUESTION:
            if IDENTIFIER in data and data[IDENTIFIER] in self.clients.keys:
                self.handle_question(data)
            else:
                logger.error('Server.py: QUESTION missing client id. Closing connection.')
                await websocket.close()

        elif message[MESSAGE_TYPE] == DECLARATION:
            if IDENTIFIER in data and data[IDENTIFIER] in self.clients.keys:
                self.handle_declaration(data)
            else:
                logger.error('Server.py: DECLARATION missing client id. Closing connection.')
                await websocket.close()

        elif message[MESSAGE_TYPE] == HANDSHAKE:
            logger.info('Connecting New Client')

    def handle_create_game_request(self, websocket: WebSocket, data: dict) -> str:
        if self.game:
            logger.info('Deleting Existing Game')
            self.game = None

        logger.info('Creating New Game')
        self.game = GameFactory.create_game(self, data)

        # TODO: improve generating server response
        return json.dumps({
            MESSAGE_TYPE: CREATED_GAME,
            DATA: {
                PIN: self.game.pin,
            }
        })

    def handle_connect_to_game_request(self, websocket: WebSocket, data: dict):
        if self.game and data[PIN] == self.game.pin:
            logger.info('Connecting User to game')

            client_id = self.register_new_client(data[NAME], websocket)

            return json.dumps({
                MESSAGE_TYPE: CONNECTED_TO_GAME,
                DATA: {
                    IDENTIFIER: client_id,
                    CARDS: self.game.players[data[NAME]].get_cards(),
                    TEAMS_KEY: self.game.teams
                }
            })
        else:
            return json.dumps({
                MESSAGE_TYPE: ERROR,
                DATA: {
                    DESCRIPTION: 'Invalid PIN'
                }
            })

    def handle_set_cards(self, data: dict):
        # check to make sure the expected fields exist
        if CARDS in data:
            logger.info('Setting client %s cards to %s.' % (data[IDENTIFIER], data[CARDS]))
            self.game.players[data[IDENTIFIER]].set_initial_cards(data[CARDS])
        else:
            raise exception(
                'Unknown Message Format: Server.py: SET_CARDS: Message does not have CARDS key')

    def handle_question(self, data: dict):
        logger.info('Received question')
        if QUESTIONER in data and RESPONDENT in data and CARD in data:
            self.game.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])
        else:
            raise exception(
                'Unknown Message Format: Server.py: QUESTION: Message does not have QUESTIONER, RESPONDENT, or CARD')

    def handle_declaration(self, data: dict):
        logger.info('Received declaration')
        card_set = card_set_for_key(data[CARD_SET])
        if PLAYER_KEY in data and CARD_SET in data and DECLARED_MAP in data and card_set.is_present():
            self.game.handle_declaration(data[PLAYER_KEY], data[CARD_SET], data[DECLARED_MAP])
        else:
            raise exception(
                'Unknown Message Format: Server.py: DECLARATION: Message does not have PLAYER_KEY, CARD_SET, or DECLARED_MAP')

    def register_new_client(self, identifier: str, websocket: WebSocket) -> str:
        logger.info('Registering new client with id: %s' % identifier)
        self.clients[identifier] = websocket
        return identifier

    # Network Delegate Implementation
    def broadcast_message(self, client_id: str, contents: dict):
        message = self.parse(contents)
        # QS: maybe change from client_id to user name? Where do we want
        # to keep another list of user names to unique client ids. These
        # client IDs will need to be different than the websocket IDs, I think.
        # TODO: come back to figure out how to register clients
        # websocket: WebSocket = self.clients[client_id]
        # if isinstance(websocket, WebSocket):
        #     websocket.send_json(message)

    @staticmethod
    def parse(message):
        if isinstance(message, str):
            return json.loads(message)
        elif isinstance(message, dict):
            return message
            # return json.dumps(message)

        return None
