from fastapi import Cookie, Depends, FastAPI, Header
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.network.NetworkManager import NetworkManager

app = FastAPI()

# TODO: not ideal and will move
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <button type="button" onClick="createGame(event)">Create Game</button>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                console.log("I receved an event")
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
            function createGame(event) {
                settings = {"players": [
                    {"name": "graham", "type": "network"},
                    {"name": "peter", "type": "network"},
                    {"name": "mikaela", "type": "network"},
                    {"name": "comp1", "type": "computer"},
                    {"name": "comp2", "type": "computer"},
                    {"name": "comp3", "type": "computer"}, ],
                "virtual_deck": True,
                "teams": [
                    {"name": "test_team_one", "players": ["graham", "peter", "mikaela"]},
                    {"name": "test_team_two", "players": ["comp1", "comp2", "comp3"]}]
                }
                
                ws.send(JSON.stringify(settings))
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


network_manager = NetworkManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await network_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = network_manager.handle_message(websocket, data)
            if message:
                await websocket.send_text(message)
    except WebSocketDisconnect:
        network_manager.remove(websocket)
