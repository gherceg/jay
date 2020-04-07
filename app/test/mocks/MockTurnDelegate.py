from app.player import TurnDelegate
from app.game.data import Turn, Declaration


class MockTurnDelegate(TurnDelegate):
    received_update = False
    turn_received: Turn

    received_declaration = False
    declaration_received: Declaration

    def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        self.received_update = True
        self.turn_received = turn

    def broadcast_declaration(self, player: str, declaration: Declaration, cards: tuple):
        self.received_declaration = True
        self.declaration_received = declaration
