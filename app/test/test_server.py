from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
client_two = TestClient(app)


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
        data = websocket.receive_json()
        assert data == expected_connect_game_response()


def create_game_json() -> dict:
    return {'type': 'create_game',
            'data': {
                'name': 'a',
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
                'identifier': 'a',
                'pin': 1234,
                'players': ['a', 'b', 'c', 'd', 'e', 'f'],
                'teams': {'team1': ['a', 'b', 'c'], 'team2': ['d', 'e', 'f']},
            }
            }


def expected_connect_game_response() -> dict:
    return {'type': 'connected_to_game',
            'data': {'identifier': 'b',
                     'cards': [],
                     }
            }
