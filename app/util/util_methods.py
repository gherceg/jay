import random
from typing import List, Set

from app.constants import *
from app.data.game_enums import CardSet
from app.util import Optional


def client_identifier(player_id: str, game_id: str) -> str:
    return f'{game_id}_{player_id}'


def eligible_sets(cards: List[str]) -> List[CardSet]:
    sets = set()
    for card in cards:
        sets.add(set_for_card(card))

    return list(sets)


def eligible_cards(cards: List[str]) -> List[str]:
    sets = eligible_sets(cards)
    all_cards_for_sets: Set[str] = set()
    for card_set in sets:
        all_cards_for_sets.update(card_set.value)

    return list(all_cards_for_sets.symmetric_difference(cards))


def set_for_card(card) -> CardSet:
    for card_set in CardSet:
        if card in card_set.value:
            return card_set
    raise ValueError('CardSet does not exist for card {0}'.format(card))


def deck_of_cards() -> List[str]:
    cards = []
    for card_set in CardSet:
        cards = [*cards, *card_set.value]
    return cards


def distribute_cards(player_count: int) -> tuple:
    if 48 % player_count != 0:
        raise ValueError("Player count must be a factor of 48")

    cards = deck_of_cards()
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


def key_for_card_set(card_set: CardSet) -> str:
    if card_set == CardSet.LOW_SPADES:
        return LOW_SPADES_KEY
    elif card_set == CardSet.HIGH_SPADES:
        return HIGH_SPADES_KEY
    elif card_set == CardSet.LOW_HEARTS:
        return LOW_HEARTS_KEY
    elif card_set == CardSet.HIGH_HEARTS:
        return HIGH_HEARTS_KEY
    elif card_set == CardSet.LOW_DIAMONDS:
        return LOW_DIAMONDS_KEY
    elif card_set == CardSet.HIGH_DIAMONDS:
        return HIGH_DIAMONDS_KEY
    elif card_set == CardSet.LOW_CLUBS:
        return LOW_CLUBS_KEY
    elif card_set == CardSet.HIGH_CLUBS:
        return HIGH_CLUBS_KEY
    else:
        raise Exception(f'CardSet {card_set} does not have defined key')
