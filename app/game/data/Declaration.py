from app.game.data.CardSet import CardSet


class Declaration:
    def __init__(self, player: str, card_set: CardSet, declared_map: dict, outcome: bool):
        self.player = player
        self.card_set = card_set
        self.declared_map = declared_map
        self.outcome = outcome

    def __repr__(self):
        if self.outcome:
            return "%s successfully declared the %s" % (
                self.player,
                self.card_set
            )
        else:
            return "%s failed to declare the %s" % (
                self.player,
                self.card_set
            )

    def to_dict(self) -> dict:
        return {'type': 'declaration',
                'player': self.player,
                'card_set': self.card_set,
                'declared_map': self.declared_map,
                'outcome': self.outcome}
