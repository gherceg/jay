from typing import Dict, List, Tuple

from app.data.game import Game
from app.data.network import Client
from app.util import Optional


class MessageResult:

    def __init__(self, game: Optional[Game] = Optional.empty(),
                 new_client: Optional[Client] = Optional.empty(),
                 messages: Optional[List[Tuple[str, Dict]]] = Optional.empty()):
        self.game = game
        self.new_client = new_client
        self.pending_messages = messages
