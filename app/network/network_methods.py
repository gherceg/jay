import logging
from starlette.websockets import WebSocket
from typing import Dict

from app.constants import *
from app.network import Client

logger = logging.getLogger(__name__)


def client_identifier(player_id: str, game_id: str) -> str:
    return f'{game_id}_{player_id}'


def websocket_identifier(websocket: WebSocket) -> str:
    return f'{websocket.client.host}:{websocket.client.port}'


async def send_error(websocket: WebSocket, message: str):
    logger.error(message)
    data = {
        MESSAGE_TYPE: ERROR,
        DATA: {
            DESCRIPTION: message
        }
    }
    await websocket.send_json(data)


async def send_message(websocket: WebSocket, data: Dict):
    logger.info('Sending {0} message to websocket {1}'.format(data[MESSAGE_TYPE], websocket.client))
    await websocket.send_json(data)
