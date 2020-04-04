from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.network.Server import Server

app = FastAPI()

server = Server()

@app.get("/")
async def read_main():
    return {"msg": "Literature Server"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await server.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = await server.handle_message(websocket, data)
            if message:
                await websocket.send_json(message)
    except WebSocketDisconnect:
        server.remove(websocket)
