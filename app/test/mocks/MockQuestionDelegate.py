from app.player import QuestionDelegate


class MockQuestionDelegate(QuestionDelegate):
    received_question: bool = False
    questioner: str = None
    respondent: str = None
    card: str = None

    def handle_question(self, questioner: str, respondent: str, card: str):
        self.received_question = True
        self.questioner = questioner
        self.respondent = respondent
        self.card = card
