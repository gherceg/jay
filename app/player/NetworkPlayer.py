from app.player import PlayerInterface, NetworkPlayerDelegate
from app.game.data import Turn, Declaration


class NetworkPlayer(PlayerInterface):
    delegate: NetworkPlayerDelegate = None

    def set_delegate(self, delegate: NetworkPlayerDelegate):
        self.delegate = delegate

    # Player Interface Methods
    async def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)
        await self.delegate.broadcast_turn(self.name, turn, self.get_cards())

    async def received_declaration(self, declaration: Declaration):
        super().received_declaration(declaration)
        await self.delegate.broadcast_declaration(self.name, declaration, self.get_cards())
