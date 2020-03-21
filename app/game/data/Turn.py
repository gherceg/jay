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
            return "%s received from %s the %s" % (
                self.questioner,
                self.respondent,
                self.card,
            )
        else:
            return "%s asked %s for the %s" % (
                self.questioner,
                self.respondent,
                self.card,
            )

    def to_dict(self) -> dict:
        return {'questioner': self.questioner,
                'respondent': self.respondent,
                'card': self.card,
                'outcome': self.outcome}
