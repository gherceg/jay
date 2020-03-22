from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_game_setup():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json(create_game_json())
        data = websocket.receive_json()
        assert data == expected_setup_response()

def create_game_json() -> dict:
    return {'type': 'setup',
            'data': {'players': [{'name': 'a', 'type': 'network'},
                                 {'name': 'b', 'type': 'network'},
                                 {'name': 'c', 'type': 'network'},
                                 {'name': 'd', 'type': 'network'},
                                 {'name': 'e', 'type': 'network'},
                                 {'name': 'f', 'type': 'network'}],
                     'teams': [{'name': 'team1', 'players': ('a', 'b', 'c')},
                               {'name': 'team2', 'players': ('d', 'e', 'f')}],
                     'virtual_deck': True
                     }
            }

def expected_setup_response() -> dict:
    return {'type': 'setup',
            'data': {'pin': 1234,
                     'players': ['a', 'b', 'c', 'd', 'e', 'f'],
                     'teams': {'team1': ['a', 'b', 'c'], 'team2': ['d', 'e', 'f']},
                     }
            }
