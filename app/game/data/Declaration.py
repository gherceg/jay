from app.game.data.CardSet import CardSet
from app.util import util_methods


class Declaration:
    def __init__(self, player: str, card_set: CardSet, declared_list: tuple, outcome: bool):
        self.player = player
        self.card_set = card_set
        self.declared_list = declared_list
        self.outcome = outcome

    def __repr__(self):
        if self.outcome:
            return "{0} successfully declared the {1}".format(self.player, self.card_set)
        else:
            return "{0} failed to declare the {1}".format(self.player, self.card_set)

    def to_dict(self) -> dict:
        return {'type': 'declaration',
                'player': self.player,
                'card_set': util_methods.key_for_card_set(self.card_set),
                'declared_map': self.declared_list,
                'outcome': self.outcome}
