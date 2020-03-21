from app.player.PlayerInterface import PlayerInterface
from app.player.TurnDelegate import *


class NetworkPlayer(PlayerInterface):
    delegate: TurnDelegate = None

    def set_turn_delegate(self, delegate: TurnDelegate):
        self.delegate = delegate

    # Player Interface Methods
    def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)
        print("Network player received a game update, informing delegate...")
        self.delegate.broadcast_turn(self.name, turn, self.get_cards())
