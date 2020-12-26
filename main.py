import logging
from typing import Any

from fastapi import FastAPI
from starlette.endpoints import WebSocketEndpoint
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from app.app_controller import AppController

# TODO improve middleware
middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

# create app and server
app = FastAPI(middleware=middleware)
controller = AppController()

# setup logging
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def read_main():
    return {"msg": "Literature Server"}


@app.websocket_route("/ws")
class WebSocket(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket) -> None:
        await controller.connect(websocket)

    async def on_receive(self, websocket: WebSocket, data: Any) -> None:
        await controller.receive(websocket, data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        controller.disconnect(websocket)
