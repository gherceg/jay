import logging
from starlette.websockets import WebSocket, WebSocketState
from typing import Dict
import asyncio

from app.message_handler import received_message
from app.data.network import Client
from app.data.app_state import MessageResult
from app.data.game import Game, Player
from app import computer_player
from app.constants import *

logger = logging.getLogger(__name__)


class AppController:
    """Entry point to application, manages I/O"""

    def __init__(self):
        # hold onto all connections
        self.connections: Dict[str, WebSocket] = {}
        # use client to identify player and game they are apart of
        self.clients: Dict[str, Client] = {}
        # hold onto game references
        self.games: Dict[int, Game] = {}

    def new_connection(self, websocket: WebSocket):
        sender: str = websocket_identifier(websocket)
        self.connections[sender] = websocket

    def remove(self, websocket: WebSocket):
        # TODO ensure websocket id is unique, it might not be
        identifier = websocket_identifier(websocket)
        for client in self.clients.values():

            if websocket_identifier in client.connections:
                client.connections.remove(identifier)
            if websocket_identifier in self.connections.keys():
                del self.connections[identifier]

    async def handle_message(self, websocket: WebSocket, data: Dict):
        sender: str = websocket_identifier(websocket)

        result: MessageResult = received_message(sender, data, self.games, self.clients)
        self.update_state_for_result(result)

        # side effect
        await self.send_pending_messages(result)

        # perfect scenario for recursion, but stack runs out of space so a loop will have to do
        while result.game.is_present() and result.game.get().up_next().is_present() and result.game.get().up_next().get().player_type == COMPUTER_PLAYER:
            await asyncio.sleep(COMPUTER_WAIT_TIME)
            computer_generated_data: Dict = computer_player.automate_turn(result.game.get())
            result: MessageResult = received_message(COMPUTER_PLAYER, computer_generated_data, self.games, self.clients)
            self.update_state_for_result(result)
            # side effect
            await self.send_pending_messages(result)

    def update_state_for_result(self, result: MessageResult):
        # update clients if necessary
        if result.new_client.is_present():
            client: Client = result.new_client.get()
            self.clients[client.identifier] = client

        # update game if necessary
        if result.game.is_present():
            updated_game: Game = result.game.get()
            logger.info(f'Updating controller game for pin {updated_game.pin}')
            self.games[updated_game.pin] = updated_game

    async def send_pending_messages(self, result: MessageResult):
        # send messages if necessary
        # TODO could cleanup a bit
        if result.pending_messages.is_present():
            for (identifier, message) in result.pending_messages.get():
                # slight hack for now
                if identifier == COMPUTER_PLAYER:
                    break

                if identifier in self.connections:
                    await send_message(self.connections[identifier], message)
                elif identifier in self.clients:
                    client: Client = self.clients[identifier]
                    for identifier in client.connections:
                        if identifier in self.connections.keys():
                            websocket: WebSocket = self.connections[identifier]
                            await send_message(websocket, message)


def websocket_identifier(websocket: WebSocket) -> str:
    return f'{websocket.client.host}:{websocket.client.port}'


async def send_message(websocket: WebSocket, message: Dict):
    try:
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_json(message)
        else:
            logger.error(f'Websocket is disconnected. Not sending message')
    except:
        # TODO figure out concurrency issue with not receiving disconnect until event loop is idle again
        #  to avoid broad exception clause, figure out a specific exception to catch.
        #  The crash is due to starlette.websockets.exceptions.ConnectionClosedOK
        logger.error('Attempted to send message to disconnected websocket.')
