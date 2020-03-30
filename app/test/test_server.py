from fastapi.testclient import TestClient

from main import app
from app.test.TestVariables import *
from app.Constants import *

client = TestClient(app)
client_two = TestClient(app)
test_variables = TestVariables(('a', 'b', 'c', 'd', 'e', 'f'))


def test_game_creation():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(create_game_json())
        data = websocket.receive_json()
        assert data == expected_create_game_response()


def test_game_connect():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(create_game_json())

    with client_two.websocket_connect("/ws") as websocket:
        websocket.send_json(connect_game_json())
        data: dict = websocket.receive_json()
        # ensure that next_turn is a valid player name
        message_data = data[DATA]
        assert message_data[NEXT_TURN] in test_variables.player_names

        for (key, value) in message_data.items():
            if key != NEXT_TURN:
                assert value == expected_connect_game_response()[DATA][key]


def create_game_json() -> dict:
    return {'type': 'create_game',
            'data': {
                'players': [{'name': 'a', 'type': 'network'},
                            {'name': 'b', 'type': 'network'},
                            {'name': 'c', 'type': 'network'},
                            {'name': 'd', 'type': 'network'},
                            {'name': 'e', 'type': 'network'},
                            {'name': 'f', 'type': 'network'}],
                'teams': [{'name': 'team1', 'players': ('a', 'b', 'c')},
                          {'name': 'team2', 'players': ('d', 'e', 'f')}],
                'virtual_deck': False
            }
            }


def connect_game_json() -> dict:
    return {'type': 'connect_to_game',
            'data': {'pin': 1234,
                     'name': 'b'}
            }


def expected_create_game_response() -> dict:
    return {'type': 'created_game',
            'data': {
                'pin': 1234,
            }
            }


def expected_connect_game_response() -> dict:
    return {'type': 'connected_to_game',
            'data': {'identifier': 'b',
                     'cards': [],
                     'teams': [{'name': 'team1', 'players': ['a', 'b', 'c']},
                               {'name': 'team2', 'players': ['d', 'e', 'f']}],
                     'next_turn': 'a'
                     }
            }
