from app.game.data.Turn import Turn
from app.player.QuestionDelegate import QuestionDelegate
from app.player.TurnDelegate import TurnDelegate
from app.network.NetworkDelegate import NetworkDelegate


class Game(QuestionDelegate, TurnDelegate):
    """Responsible for managing a game and its players"""

    # TODO: these items need to be included in the constructor if we don't want them to persist
    pin: int = 1234
    players: dict = {}
    teams: dict = {}
    ledger: list = []

    def __init__(self, network_delegate: NetworkDelegate, players: tuple, teams: tuple):
        self.network_delegate = network_delegate
        self.pin = 1234
        self.ledger = []

        # create a dictionary of players for easy lookup
        self.players = {}
        for player in players:
            self.players[player.name] = player

        self.teams = {}
        for team in teams:
            self.teams[team['name']] = team['players']

    def handle_question(self, questioner: str, respondent: str, card: str):
        outcome = self.does_player_have_card(respondent, card)
        turn = Turn(questioner, respondent, card, outcome)
        self.ledger.append(turn)
        for key, player in self.players.items():
            player.received_next_turn(turn)

    def broadcast_turn(self, player: str, turn: Turn, cards: tuple):
        """Package update to send to client"""
        contents = {}
        contents['message_type'] = 'game_update'
        contents['game_id'] = 0
        contents['last_turn'] = turn.to_dict()
        contents['cards'] = cards
        # contents['current_turn'] = self.game.up_next
        contents['teams'] = self.build_teams_package()

        self.network_delegate.broadcast_message(player, contents)

    def get_player_names(self):
        return list(self.players.keys())

    # PRIVATE METHODS

    def does_player_have_card(self, player_name: str, card: str):
        if player_name not in self.players.keys():
            raise ValueError(f"Player {player_name} not found in game")
        return self.players[player_name].has_card(card)

    def build_teams_package(self) -> dict:
        teams_dict = {}
        for name, players in self.teams.items():
            team_players = []
            for player_name in players:
                player_dict = {
                    'name': player_name,
                    'card_count': len(self.players[player_name].get_cards())
                }
                team_players.append(player_dict)
            teams_dict[name] = team_players
        return teams_dict
