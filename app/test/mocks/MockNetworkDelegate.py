from app.network.NetworkDelegate import NetworkDelegate


class MockNetworkDelegate(NetworkDelegate):
    client_id: str = False
    contents: dict = None

    def broadcast_message(self, client_id: str, contents: dict):
        self.client_id = client_id
        self.contents = contents
