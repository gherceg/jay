from typing import List, Tuple

from app.constants import *
from app.data.game_enums import CardSet
from app.util import util_methods


class Declaration:
    def __init__(self, player: str, card_set: CardSet, declared_list: List[Tuple[str, str]], outcome: bool):
        self.player: str = player
        self.card_set: CardSet = card_set
        self.declared_list: List[Tuple[str, str]] = declared_list
        self.outcome: bool = outcome

    def __repr__(self):
        if self.outcome:
            return "{0} successfully declared the {1}".format(self.player, self.card_set)
        else:
            return "{0} failed to declare the {1}".format(self.player, self.card_set)

    def to_dict(self) -> dict:
        return {TYPE: DECLARATION,
                PLAYER: self.player,
                CARD_SET: util_methods.key_for_card_set(self.card_set),
                DECLARED_MAP: self.declared_list,
                OUTCOME: self.outcome}


class Question:
    def __init__(
            self,
            questioner: str,
            respondent: str,
            card: str,
            outcome: bool,
    ):
        self.questioner = questioner
        self.respondent = respondent
        self.card = card
        self.outcome = outcome

    def __repr__(self):
        if self.outcome:
            return "{0} received from {1} the {2}".format(self.questioner, self.respondent, self.card)
        else:
            return "{0} asked {1} for the {2}".format(self.questioner, self.respondent, self.card)

    def to_dict(self) -> dict:
        return {TYPE: TURN,  # TODO change to question
                QUESTIONER: self.questioner,
                RESPONDENT: self.respondent,
                CARD: self.card,
                OUTCOME: self.outcome}
