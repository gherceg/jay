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


def test_enter_pin():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(create_game_json())

    with client_two.websocket_connect("/ws") as websocket:
        websocket.send_json(enter_pin_json())
        data: dict = websocket.receive_json()
        # ensure that next_turn is a valid player name
        message_data = data[DATA]
        assert message_data[NEXT_TURN] in test_variables.player_names

        for (key, value) in message_data.items():
            if key != NEXT_TURN:
                assert value == expected_joined_game_response()[DATA][key]


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


def enter_pin_json() -> dict:
    return {'type': 'enter_pin',
            'data': {'pin': 1234}
            }


def select_player_json() -> dict:
    return {'type': 'select_player',
            'data': {
                'name': 'a',
                'cards': ['9h', '10h', 'jh', 'qh', 'kh', 'ah', '2s', '3s']
            }
            }


def expected_create_game_response() -> dict:
    return {'type': 'created_game',
            'data': {
                'pin': 1234,
            }
            }


def expected_joined_game_response() -> dict:
    return {'type': 'joined_game',
            'data': {'teams': [{'name': 'team1', 'players': ['a', 'b', 'c']},
                               {'name': 'team2', 'players': ['d', 'e', 'f']}],
                     'next_turn': 'a'
                     }
            }


def expected_selected_player_response() -> dict:
    return {'type': 'selected_player',
            'data': {'identifier': 'a',
                     'cards': ['9h', '10h', 'jh', 'qh', 'kh', 'ah', '2s', '3s'],
                     }
            }
