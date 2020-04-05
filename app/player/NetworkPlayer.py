from app.player.PlayerInterface import PlayerInterface
from app.player.TurnDelegate import *
from app.game.data.Declaration import Declaration


class NetworkPlayer(PlayerInterface):
    delegate: TurnDelegate = None

    def set_turn_delegate(self, delegate: TurnDelegate):
        self.delegate = delegate

    # Player Interface Methods
    async def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)
        await self.delegate.broadcast_turn(self.name, turn, self.get_cards())

    async def received_declaration(self, declaration: Declaration):
        super().received_declaration(declaration)
        await self.delegate.broadcast_declaration(self.name, declaration, self.get_cards())



