from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
import logging

from app.network.Server import Server

app = FastAPI()

server = Server()

logging.basicConfig(level=logging.INFO)
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
            # if message:
            #     logger.info(message)
            #     await websocket.send_json(message)
    except WebSocketDisconnect:
        server.remove(websocket)
