import abc


class QuestionDelegate(abc.ABC):

    @abc.abstractmethod
    def handle_question(self, questioner: str, respondent: str, card: str):
        pass
