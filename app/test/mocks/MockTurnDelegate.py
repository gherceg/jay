from app.player.TurnDelegate import TurnDelegate
from app.game.data.Turn import Turn


class MockTurnDelegate(TurnDelegate):
    received_update: bool = False
    turn_received: Turn

    def broadcast_turn(self, turn: Turn):
        self.received_update = True
        self.turn_received = turn
