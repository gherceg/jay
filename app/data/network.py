from typing import List

from app.util.util_methods import client_identifier


class Client:
    def __init__(self, game_id: str, player_id: str):
        self.connections: List[str] = []
        self.game_id = game_id
        self.player_id = player_id

    @property
    def identifier(self) -> str:
        return client_identifier(self.player_id, self.game_id)

    def __repr__(self):
        return f'Game ID: {self.game_id}\nPlayer ID: {self.player_id}\n# of Connections: {len(self.connections)}'
