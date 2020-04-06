import random

from app.game.data.CardSet import CardSet
from app.constants import *
from app.util.Optional import Optional


def set_for_card(card) -> CardSet:
    for card_set in CardSet:
        if card in card_set.value:
            return card_set
    raise ValueError('CardSet does not exist for card {0}'.format(card))


def deck_of_cards() -> tuple:
    cards = []
    for card_set in CardSet:
        cards = [*cards, *card_set.value]
    return tuple(cards)


def distribute_cards(player_count: int) -> tuple:
    if 48 % player_count != 0:
        raise ValueError("Player count must be a factor of 48")

    cards = list(deck_of_cards())
    # shuffle deck
    random.shuffle(cards)
    # determine number of cards per player
    cards_per_player: int = 48 // player_count
    # divide into equal parts
    hands = [cards[x:x + cards_per_player] for x in range(0, len(cards), cards_per_player)]

    assert len(hands) == player_count
    return tuple(hands)


def card_set_for_key(key: str) -> Optional:
    if key == LOW_CLUBS_KEY:
        return Optional(CardSet.LOW_CLUBS)
    elif key == HIGH_CLUBS_KEY:
        return Optional(CardSet.HIGH_CLUBS)
    elif key == LOW_DIAMONDS_KEY:
        return Optional(CardSet.LOW_DIAMONDS)
    elif key == HIGH_DIAMONDS_KEY:
        return Optional(CardSet.HIGH_DIAMONDS)
    elif key == LOW_SPADES_KEY:
        return Optional(CardSet.LOW_SPADES)
    elif key == HIGH_SPADES_KEY:
        return Optional(CardSet.HIGH_SPADES)
    elif key == LOW_HEARTS_KEY:
        return Optional(CardSet.LOW_HEARTS)
    elif key == HIGH_HEARTS_KEY:
        return Optional(CardSet.HIGH_HEARTS)
    else:
        return Optional.empty()
