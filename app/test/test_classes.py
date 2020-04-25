from typing import Dict

from app.data.network_data import NetworkDelegate


class TestVariables:

    def __init__(self, player_names: tuple):
        self.player_names = player_names


class MockNetworkDelegate(NetworkDelegate):
    client_id: str = False
    contents: dict = None

    def broadcast_message(self, client_id: str, contents: Dict):
        self.client_id = client_id
        self.contents = contents
