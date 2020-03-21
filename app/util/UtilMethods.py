import random

from app.game.data.CardSet import CardSet


def set_for_card(card) -> CardSet:
    for card_set in CardSet:
        if card in card_set.value:
            return card_set
    raise ValueError("CardSet does not exist for card %s" % card)


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
