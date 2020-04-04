import logging
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
    """Inspects incoming messages to determine which game to update, and sends messages back to clients"""

    def __init__(self):
        self.connections: list = []
        self.clients: dict = {}
        self.game = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        logger.info('Connected new client %s' % websocket.client)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)
        logger.info('Disconnecting client %s' % websocket.client)

    async def handle_message(self, websocket: WebSocket, message: str) -> str:
        message = self.parse(message)
        if message.is_empty():
            return self.generate_error('Cannot parse message: Received unexpected format.')

        logger.debug('Received message from client: %s' % message)

        if MESSAGE_TYPE not in message:
            return self.generate_error('Cannot parse message: Missing message_type field')

        if DATA not in message:
            return self.generate_error('Cannot parse message: Missing data field')

        data = message[DATA]

        if message[MESSAGE_TYPE] == CREATE_GAME:
            return self.handle_create_game_request(data)

        elif message[MESSAGE_TYPE] == ENTER_PIN:
            return self.handle_enter_pin_request(data)

        elif message[MESSAGE_TYPE] == SELECT_PLAYER:
            self.handle_select_player_request(websocket, data)

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

    def handle_create_game_request(self, data: dict) -> str:
        if self.game:
            logger.info('Deleting Existing Game')
            self.game = None

        self.game = GameFactory.create_game(self, data)
        logger.info('Create Game Request: created new game with pin %s' % self.game.pin)

        return json.dumps({
            MESSAGE_TYPE: CREATED_GAME,
            DATA: {
                PIN: self.game.pin,
            }
        })

    def handle_enter_pin_request(self, data: dict) -> str:
        if PIN in data:
            if self.game and data[PIN] == self.game.pin:
                return json.dumps({
                    MESSAGE_TYPE: JOINED_GAME,
                    DATA: {
                        TEAMS_KEY: self.game.get_teams_json(),
                        NEXT_TURN: self.game.up_next
                    }
                })
            else:
                return self.generate_error('Enter Pin Request: Invalid pin')
        else:
            return self.generate_error('Enter Pin Request: Missing pin field')

    def handle_select_player_request(self, websocket: WebSocket, data: dict) -> str:
        # check to make sure the expected fields exist
        if NAME in data:
            client_id = self.register_new_client(data[NAME], websocket)
            if self.game.virtual_deck is False:
                if CARDS in data:
                    self.game.players[data[NAME]].set_initial_cards(data[CARDS])
                else:
                    return self.generate_error('Select Player Request: Missing cards field')

            return json.dumps({
                MESSAGE_TYPE: SELECTED_PLAYER,
                DATA: {
                    IDENTIFIER: client_id,
                    CARDS: self.game.players[data[NAME]].get_cards(),
                }
            })
        else:
            return self.generate_error('Select Player Request: Missing name field')

    def handle_question(self, data: dict):
        logger.info('Received question')
        if QUESTIONER in data and RESPONDENT in data and CARD in data:
            self.game.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])
        else:
            return self.generate_error('Question Request: Missing questioner, respondent or card field')

    def handle_declaration(self, data: dict):
        logger.info('Received declaration')
        card_set = card_set_for_key(data[CARD_SET])
        if PLAYER_KEY in data and CARD_SET in data and DECLARED_MAP in data and card_set.is_present():
            self.game.handle_declaration(data[PLAYER_KEY], data[CARD_SET], data[DECLARED_MAP])
        else:
            return self.generate_error('Declaration Request: Missing player, card_set or declared_map field')

    def register_new_client(self, identifier: str, websocket: WebSocket) -> str:
        logger.info('Registering new client with id: %s' % identifier)
        self.clients[identifier] = websocket
        return identifier

    @staticmethod
    def generate_error(message: str) -> str:
        logger.error(message)
        return json.dumps({
            MESSAGE_TYPE: ERROR,
            DATA: {
                DESCRIPTION: message
            }
        })

    @staticmethod
    def parse(message) -> Optional:
        if isinstance(message, str):
            return Optional(json.loads(message))
        elif isinstance(message, dict):
            return Optional(message)
            # return json.dumps(message)

        return Optional.empty()

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
