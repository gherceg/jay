from app.player import ComputerPlayerDelegate
from app.game.data import CardSet


class MockComputerPlayerDelegate(ComputerPlayerDelegate):
    received_question: bool = False
    questioner: str = None
    respondent: str = None
    card: str = None

    declaring_player: str = None
    declared_set: CardSet = None
    declared_map: tuple = None

    async def handle_question(self, questioner: str, respondent: str, card: str):
        self.received_question = True
        self.questioner = questioner
        self.respondent = respondent
        self.card = card

    async def computer_generated_declaration(self, player: str, card_set: CardSet, declared_map: tuple):
        self.declaring_player = player
        self.declared_set = card_set
        self.declared_map = declared_map

    def get_next_turn(self) -> str:
        return "test"
