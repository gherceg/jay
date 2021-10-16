from typing import Dict, List, Optional, Tuple

from app.data.game import Game
from app.data.network import Client


class MessageResult:

    def __init__(self, game: Optional[Game] = None,
                 new_client: Optional[Client] = None,
                 messages: Optional[List[Tuple[str, Dict]]] = None):
        self.game = game
        self.new_client = new_client
        self.pending_messages = messages
