from app.game.data.CardStatus import CardStatus
from app.game.data.Turn import Turn
from app.game.data.Declaration import Declaration
from app.game.data.CardSet import CardSet
from app.util.UtilMethods import set_for_card, deck_of_cards
from app.util.DataFrameMethods import *


class StateMethods:

    @staticmethod
    def create_default_state(players: tuple) -> DataFrame:
        """Creates and returns a DataFrame object that contains a column for each player and a row for each card
            Each cell is set to the CardStatus UNKNOWN
        """
        cards = deck_of_cards()
        return create_state_with_value(cards, players, CardStatus.UNKNOWN)

    @staticmethod
    def update_state_upon_receiving_cards(state: DataFrame, player: str, cards: tuple):
        """Update column for player to DOES_HAVE for all cards specified, and DOES_NOT_HAVE for remaining rows"""

        # start by setting player's entire column to does not have
        state.loc[:, player] = CardStatus.DOES_NOT_HAVE

        # for the cards specified, set every player to does not have as well
        for card in cards:
            # error check - ensure that no other player already lists having this card
            if any(state.loc[card, :] == CardStatus.DOES_HAVE):
                # return error - INVALID CARD STATE
                raise Exception('Invalid Card Entry. A Card was already assigned to another player.')
            else:
                state.loc[card, :] = CardStatus.DOES_NOT_HAVE

        # finally, update specified cards to does have for player specified
        for card in cards:
            state.loc[card, player] = CardStatus.DOES_HAVE

        return state

    @staticmethod
    def update_state_with_turn(state: DataFrame, turn: Turn) -> DataFrame:
        card_set: CardSet = set_for_card(turn.card)

        if turn.outcome:
            # we know which player has the card so the rest do not
            state.loc[turn.card, :] = CardStatus.DOES_NOT_HAVE
            state.loc[turn.card, turn.questioner] = CardStatus.DOES_HAVE
        else:
            # we know that both players do not have the given card
            state.loc[turn.card, turn.questioner] = CardStatus.DOES_NOT_HAVE
            state.loc[turn.card, turn.respondent] = CardStatus.DOES_NOT_HAVE

        # update any unknown statuses to might have for the player asking the question
        state = update_rows_with_old_to_new_for_column(state,
                                                       card_set.value,
                                                       turn.questioner,
                                                       CardStatus.UNKNOWN,
                                                       CardStatus.MIGHT_HAVE)
        return state

    @staticmethod
    def update_state_with_declaration(state: DataFrame, declaration: Declaration) -> DataFrame:
        for card in declaration.declared_map.keys():
            state.loc[card, :] = CardStatus.DECLARED

        return state

    @staticmethod
    def get_cards_for_player(state: DataFrame, player: str) -> tuple:
        card_rows = state.loc[:, player]
        cards = card_rows[card_rows == CardStatus.DOES_HAVE]
        return tuple(cards.keys())
