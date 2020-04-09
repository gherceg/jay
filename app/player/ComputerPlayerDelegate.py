import abc

from app.game.data import CardSet


class ComputerPlayerDelegate(abc.ABC):

    @abc.abstractmethod
    def get_next_turn(self) -> str:
        pass

    @abc.abstractmethod
    async def handle_question(self, questioner: str, respondent: str, card: str):
        pass

    @abc.abstractmethod
    async def computer_generated_declaration(self, player: str, card_set: CardSet, declared_map: tuple):
        pass
