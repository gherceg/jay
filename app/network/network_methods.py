import logging

from starlette.websockets import WebSocket
from typing import Dict

from app.constants import *

logger = logging.getLogger(__name__)


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
    logger.info('Sending message to websocket {0}: {1}'.format(websocket.client, data))
    await websocket.send_json(data)