class Turn:
    def __init__(
            self,
            questioner: str,
            respondent: str,
            card: str,
            outcome: bool,
    ):
        self.questioner = questioner
        self.respondent = respondent
        self.card = card
        self.outcome = outcome

    def __repr__(self):
        if self.outcome:
            return "{0} received from {1} the {2}".format(self.questioner, self.respondent, self.card)
        else:
            return "{0} asked {1} for the {2}".format(self.questioner, self.respondent, self.card)

    def to_dict(self) -> dict:
        return {'type': 'turn',
                'questioner': self.questioner,
                'respondent': self.respondent,
                'card': self.card,
                'outcome': self.outcome}
