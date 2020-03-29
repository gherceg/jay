from app.player.PlayerInterface import PlayerInterface
from app.player.StateMethods import *
from app.player.QuestionDelegate import QuestionDelegate


class ComputerPlayer(PlayerInterface):
    delegate: QuestionDelegate = None

    def set_question_delegate(self, delegate: QuestionDelegate):
        self.delegate = delegate

    def received_next_turn(self, turn: Turn):
        super().received_next_turn(turn)

    def received_declaration(self, declaration: Declaration):
        super().received_declaration(declaration)