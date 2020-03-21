from network.NetworkDelegate import NetworkDelegate
from starlette.websockets import WebSocket, WebSocketDisconnect
import json
from game.GameFactory import GameFactory
from game.Game import Game
import logging
from Constants import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkManager(NetworkDelegate):
    """Holds onto websocket connections"""
    game: Game = None

    # Network Delegate Implementation
    def broadcast_message(self, client_id: str, contents: dict):
        message = self.parse(contents)
        # QS: Where does this get called?
        # QS: maybe change from client_id to user name? Where do we want 
        # to keep another list of user names to unique client ids. These 
        # client IDs will need to be different than the websocket IDs, I think.
        # TODO: come back to figure out how to register clients
        # websocket: WebSocket = self.clients[client_id]
        # if isinstance(websocket, WebSocket):
        #     websocket.send_json(message)

    def __init__(self):
        self.connections: list = []
        self.clients: dict = {}
        self.generator = self.get_notification_generator()

    def handle_message(self, websocket: WebSocket, message: str) -> str:
        message = self.parse(message)
        logger.debug(message)
        if DATA in message:
            data = message[DATA]
        else:
            raise exception('Unknown Message Format: NetworkManager.py: No DATA field found in message.')

        if MESSAGE_TYPE not in message:
            raise exception('Unknown Message Format: NetworkManager.py: No MESSAGE_TYPE field found in message.')

        if message[MESSAGE_TYPE] == GAME_SETUP_KEY:
            if self.game:
                logger.info('Deleting Existing Game...')
                self.game = None
                
            logger.info('Creating New Game...')
            # TODO: need a client id for this websocket. Should it be sent in the message?
            # self.clients['host'] = websocket
            self.game = GameFactory.create_game(self, data)
            # TODO: decide how we want to send this information back formally? 
            # Should there be another class to handle it?
            return json.dumps({
                'type': 'setup',
                'data': {
                    'pin': self.game.pin,
                    'players': self.game.get_player_names(),
                    'teams': self.game.teams,
                    }
                })

        elif message[MESSAGE_TYPE] == CONNECT_KEY:
            
            if ID in message:
                logger.info('Registering User to list of clients')
                self.clients[message[ID]] = {
                    'websocket': websocket,
                    'name': data[NAME]
                }
            
            if self.game and data[PIN] == self.game.pin:
                logger.info('Connecting User to game')
                # TODO: determine where to do error checking that the name of the person joining matches the players in the game
                # self.clients[data[NAME]] = websocket
                return json.dumps({
                    'type': 'cards',
                    'data': {
                        'name': data[NAME],
                        'cards': self.game.players[data[NAME]].get_cards()
                    }    
                })
                # return self.game.players[data[NAME]].get_cards()
            else:
                return json.dumps({
                    'type': 'error',
                    'data': {
                        'stack': 'NetworkManager.py: handle_message: line 71',
                        'message': 'Unable to connect to game with provided PIN.'
                    }
                })
                # raise exception('Error: NetworkManager.py: Unable to connect to game with provided PIN.')

        elif message[MESSAGE_TYPE] == SET_CARDS_KEY:
            logger.info('Handling player updating cards')
            # check to make sure the expected fields exist
            if PLAYER_KEY in data and CARDS in data:
                self.game.players[data[PLAYER_KEY]].set_initial_cards(cards=data[CARDS])
            else:
                raise exception('Unknown Message Format: NetworkManager.py: SET_CARDS_KEY: Message does not have PLAYER_KEY or CARDS')

        elif message[MESSAGE_TYPE] == QUESTION_KEY:
            logger.info('Handling question...')
            if QUESTIONER in data and RESPONDENT in data and CARD in data:
                self.game.handle_question(data[QUESTIONER], data[RESPONDENT], data[CARD])
            else:
                raise exception('Unknown Message Format: NetworkManager.py: QUESTION_KEY: Message does not have QUESTIONER, RESPONDENT, or CARD')                
            return "I handled the question"

        elif message[MESSAGE_TYPE] == HANDSHAKE_KEY:
            logger.info('Connecting New Client...')
            if ID in data:
                self.clients[data[ID]] = websocket

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections

    def parse(self, message):
        if isinstance(message, str):
            return json.loads(message)
        elif isinstance(message, dict):
            return message
            # return json.dumps(message)

        return None
