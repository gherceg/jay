from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.endpoints import WebSocketEndpoint
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import logging
from typing import Any

from app.network import Server

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

app = FastAPI(middleware=middleware)

server = Server()

logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def read_main():
    return {"msg": "Literature Server"}


@app.websocket_route("/ws")
class WebSocket(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket) -> None:
        logger.info(f'Connected websocket {websocket.client}')
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: Any) -> None:
        logger.info(f'Received message from websocket {websocket.client}')
        await server.handle_message(websocket, data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        logger.info(f'Disconnected websocket {websocket.client}')
        server.remove(websocket)
