from app.game import game_builder
from app.player import NetworkPlayer, ComputerPlayer
from app.test.mocks.MockTurnDelegate import MockTurnDelegate
from app.test.mocks.MockQuestionDelegate import MockQuestionDelegate

mock_network_delegate = MockTurnDelegate()
mock_question_delegate = MockQuestionDelegate()


def test_network_player_setup():
    player_info = ({
        "players": ({"name": "Graham", "type": "network"},
                    {"name": "Peter", "type": "network"},
                    {"name": "Mikaela", "type": "network"},
                    {"name": "Toby", "type": "network"},
                    {"name": "Rebecca", "type": "network"},
                    {"name": "Alicia", "type": "network"})
    })

    teams = ({"name": "team_one", "players": ["Graham", "Peter", "Mikaela"]},
             {"name": "team_two", "players": ["Toby", "Rebecca", "Alicia"]})

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        assert isinstance(player, NetworkPlayer)


def test_computer_player_setup():
    player_info = ({
        "players": ({"name": "Graham", "type": "computer"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = ({"name": "team_one", "players": ["Graham", "Peter", "Mikaela"]},
             {"name": "team_two", "players": ["Toby", "Rebecca", "Alicia"]})

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        assert isinstance(player, ComputerPlayer)


def test_player_setup_invalid_type_raises_exception():
    player_info = ({
        "players": ({"name": "Graham", "type": "invalid"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = ({"name": "team_one", "players": ["Graham", "Peter", "Mikaela"]},
             {"name": "team_two", "players": ["Toby", "Rebecca", "Alicia"]})
    try:
        players = game_builder.setup_players(player_info, teams)
    except ValueError:
        assert True
    else:
        assert False


def test_opposing_teams():
    player_info = ({
        "players": ({"name": "Graham", "type": "computer"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = ({"name": "team_one", "players": ["Graham", "Peter", "Mikaela"]},
             {"name": "team_two", "players": ["Toby", "Rebecca", "Alicia"]})

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        if player.name in teams[0]['players']:
            assert player.opposing_team == ("Toby", "Rebecca", "Alicia")
        elif player.name in teams[1]['players']:
            assert player.opposing_team == ("Graham", "Peter", "Mikaela")
        else:
            assert False


def test_teammates():
    player_info = ({
        "players": ({"name": "Graham", "type": "computer"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = ({"name": "team_one", "players": ["Graham", "Peter", "Mikaela"]},
             {"name": "team_two", "players": ["Toby", "Rebecca", "Alicia"]})

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        if player.name == "Graham":
            assert player.teammates == ("Peter", "Mikaela")
        elif player.name == "Toby":
            assert player.teammates == ("Rebecca", "Alicia")


def test_setup_teams():
    settings = ({
        "players": ({"name": "Graham", "type": "computer"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = game_builder.setup_teams(settings)

    assert set(teams[0]['players']).isdisjoint(teams[1]['players'])
    assert len(teams[0]['players']) == 3
    assert len(teams[1]['players']) == 3
