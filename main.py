from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import logging

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await server.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await server.handle_message(websocket, data)
    except WebSocketDisconnect:
        server.remove(websocket)
