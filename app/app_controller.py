import asyncio
import logging
from typing import Dict

from starlette.websockets import WebSocket, WebSocketState

from app.computer import computer_controller
from app.constants import *
from app.data.app_state import MessageResult
from app.data.game import Game
from app.data.network import Client
from app.messages.message_handler import received_message

logger = logging.getLogger(__name__)


class AppController:
    """
    The entry point to the application

    ...

    Attributes
    ----------
    connections : Dict[str, WebSocket]
        a dictionary containing active connections
    clients : Dict[str, Client]
        a dictionary containing clients
    games : Dict[int, Game]
        a dictionary containing active games stored by pin

    Methods
    -------
    connect(websocket)
        accepts connection and updates connections dictionary

    disconnect(websocket)
        updates connections and clients dictionaries

    receive(websocket, data)
        handles message, updates state based on result, potentially sends messages back to sender or all clients in game
    """

    def __init__(self):
        """Setup state for application"""
        # store connections to access when sending message back to client
        self.connections: Dict[str, WebSocket] = {}
        # maps player identifier to websocket connections
        self.clients: Dict[str, Client] = {}
        # map game pin to game object
        self.games: Dict[int, Game] = {}

    async def connect(self, websocket: WebSocket):
        """Handle websocket attempt to connect"""

        sender: str = websocket_identifier(websocket)
        self.connections[sender] = websocket

        logger.debug(f'Connected websocket {websocket.client}')
        await websocket.accept()

    def disconnect(self, websocket: WebSocket):
        """Handle websocket disconnect"""

        logger.info(f'Received disconnect from websocket { websocket_identifier(websocket)}')
        self._remove_connection(websocket)

    async def receive(self, websocket: WebSocket, data: Dict):
        """Handle receiving message from websocket"""

        logger.debug(f'Received message from websocket {websocket.client}')

        sender: str = websocket_identifier(websocket)

        result: MessageResult = received_message(sender, data, self.games, self.clients)
        self._update_state_for_result(result)

        # side effect
        await self._send_pending_messages(result)

        # perfect scenario for recursion, but stack runs out of space so a loop will have to do
        while result.game.is_present() and result.game.get().up_next().is_present() and result.game.get().up_next().get().player_type == COMPUTER_PLAYER:
            await asyncio.sleep(COMPUTER_WAIT_TIME)
            computer_generated_data: Dict = computer_controller.automate_turn(result.game.get())
            result: MessageResult = received_message(COMPUTER_PLAYER, computer_generated_data, self.games, self.clients)
            self._update_state_for_result(result)
            # side effect
            await self._send_pending_messages(result)

    def _update_state_for_result(self, result: MessageResult):
        """Internal method for updating client and game dictionaries based on message result"""

        # update clients if necessary
        if result.new_client.is_present():
            client: Client = result.new_client.get()
            self.clients[client.identifier] = client

        # update game if necessary
        if result.game.is_present():
            updated_game: Game = result.game.get()
            logger.info(f'Updating controller game for pin {updated_game.pin}')
            self.games[updated_game.pin] = updated_game

    async def _send_pending_messages(self, result: MessageResult):
        """Internal method that transforms message result into websocket and message to send"""

        # send messages if necessary
        # TODO could cleanup a bit
        if result.pending_messages.is_present():
            for (identifier, message) in result.pending_messages.get():
                # slight hack for now to avoid sending message to computer
                if identifier == COMPUTER_PLAYER:
                    break

                if identifier in self.connections:
                    await self.send_message(self.connections[identifier], message)

                elif identifier in self.clients:
                    client: Client = self.clients[identifier]
                    for client_identifier in client.connections:
                        if client_identifier in self.connections.keys():
                            websocket: WebSocket = self.connections[client_identifier]
                            await self.send_message(websocket, message)

    def _remove_connection(self, websocket: WebSocket):
        """Internal method that removes connection by identifier"""

        # TODO ensure websocket id is unique, it might not be
        identifier: str = websocket_identifier(websocket)
        for client in self.clients.values():
            if identifier in client.connections:
                logger.info(f'Removing connection {identifier} from client {client.identifier} connections')
                client.connections.remove(identifier)

            if identifier in self.connections.keys():
                logger.info(f'Removing connection {identifier} from connections')
                del self.connections[identifier]

    async def send_message(self, websocket: WebSocket, message: Dict) -> bool:
        """Internal method that attempts to send message to websocket

        Important to note that a websocket disconnect is not reliably received when the event actually occurs.
        Therefore, we must anticipate attempting to send a message to a disconnected websocket that is still believed
        to be connected. The exception thrown is starlette.websockets.exceptions.ConnectionClosedOK which is not
        publicly accessible. A broad except must be used to keep the application from crashing.
        """

        try:
            if websocket.application_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
                return True
            else:
                logger.error(f'Websocket is disconnected. Not sending message.')
                self._remove_connection(websocket)
                return False
        except:
            logger.error('Attempted to send message to disconnected websocket.')
            self._remove_connection(websocket)
            return False


def websocket_identifier(websocket: WebSocket) -> str:
    """Method used to build websocket identifier from WebSocket object"""

    return f'{websocket.client.host}:{websocket.client.port}'
