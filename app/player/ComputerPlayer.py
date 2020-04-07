from app.player import PlayerInterface, QuestionDelegate
from app.game.data import Turn, Declaration


class ComputerPlayer(PlayerInterface):
    delegate: QuestionDelegate = None

    def set_question_delegate(self, delegate: QuestionDelegate):
        self.delegate = delegate

    def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)

    def received_declaration(self, declaration: Declaration):
        super().received_declaration(declaration)
