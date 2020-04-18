from typing import Dict

from app.network import NetworkDelegate


class MockNetworkDelegate(NetworkDelegate):
    client_id: str = False
    contents: dict = None

    def broadcast_message(self, client_id: str, contents: Dict):
        self.client_id = client_id
        self.contents = contents
