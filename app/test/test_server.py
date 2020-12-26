from typing import Dict

from fastapi.testclient import TestClient

from app.constants import *
from app.test.test_classes import TestVariables
from main import app

client = TestClient(app)
client_two = TestClient(app)
test_variables = TestVariables(('a', 'b', 'c', 'd', 'e', 'f'))


def test_game_creation():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(create_game_json())
        expected_response: Dict = expected_create_game_response()
        actual_response: Dict = websocket.receive_json()
        assert actual_response[TYPE] == expected_response[TYPE]
        assert DATA in actual_response
        assert PIN in actual_response[DATA].keys()
        assert isinstance(actual_response[DATA][PIN], int)


def test_enter_pin():
    pin: int
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(create_game_json())
        response: Dict = websocket.receive_json()
        pin = response[DATA][PIN]

    with client_two.websocket_connect("/ws") as websocket:
        websocket.send_json(enter_pin_json(pin))
        expected: Dict = expected_joined_game_response()
        actual: Dict = websocket.receive_json()
        assert actual[TYPE] == expected[TYPE]
        assert DATA in actual
        assert actual[DATA].keys() == expected[DATA].keys()


def create_game_json() -> dict:
    return {'type': 'create_game',
            'data': {
                'players': [{'name': 'a', 'type': 'network', 'team': 'team1'},
                            {'name': 'b', 'type': 'network', 'team': 'team1'},
                            {'name': 'c', 'type': 'network', 'team': 'team1'},
                            {'name': 'd', 'type': 'network', 'team': 'team2'},
                            {'name': 'e', 'type': 'network', 'team': 'team2'},
                            {'name': 'f', 'type': 'network', 'team': 'team2'}],
                'teams': [{'name': 'team1', 'players': ('a', 'b', 'c')},
                          {'name': 'team2', 'players': ('d', 'e', 'f')}],
                'virtual_deck': False
            }
            }


def enter_pin_json(pin: int = 1234) -> dict:
    return {'type': 'enter_pin',
            'data': {'pin': pin}
            }


def select_player_json(pin: int = 1234) -> dict:
    return {'type': 'select_player',
            'data': {
                'pin': pin,
                'name': 'a',
                'cards': ['9h', '10h', 'jh', 'qh', 'kh', 'ah', '2s', '3s']
            }
            }


def expected_create_game_response() -> Dict:
    return {'type': 'created_game',
            'data': {
                'pin': 1234,
            }
            }


def expected_joined_game_response() -> Dict:
    return {'type': 'joined_game',
            'data': {'pin': 1234,
                     'teams': [{'name': 'team1', 'players': ['a', 'b', 'c']},
                               {'name': 'team2', 'players': ['d', 'e', 'f']}],
                     }
            }


def expected_selected_player_response() -> dict:
    return {'type': 'selected_player',
            'data': {'identifier': 'a',
                     'cards': ['9h', '10h', 'jh', 'qh', 'kh', 'ah', '2s', '3s'],
                     }
            }
