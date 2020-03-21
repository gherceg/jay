from enum import Enum


class CardSet(Enum):
    LOW_SPADES = ('2s', '3s', '4s', '5s', '6s', '7s')
    LOW_CLUBS = ('2c', '3c', '4c', '5c', '6c', '7c')
    LOW_DIAMONDS = ('2d', '3d', '4d', '5d', '6d', '7d')
    LOW_HEARTS = ('2h', '3h', '4h', '5h', '6h', '7h')
    HIGH_SPADES = ('9s', '10s', 'js', 'qs', 'ks', 'as')
    HIGH_CLUBS = ('9c', '10c', 'jc', 'qc', 'kc', 'ac')
    HIGH_DIAMONDS = ('9d', '10d', 'jd', 'qd', 'kd', 'ad')
    HIGH_HEARTS = ('9h', '10h', 'jh', 'qh', 'kh', 'ah')
