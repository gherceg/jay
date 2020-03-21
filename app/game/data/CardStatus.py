from enum import Enum


class CardStatus(Enum):
    UNKNOWN = 0
    DOES_NOT_HAVE = 1
    MIGHT_HAVE = 2
    DOES_HAVE = 3
    DECLARED = 4
