from app import game_builder
from app.data import Team
from app.constants import *


def test_network_player_setup():
    player_info = ({
        "players": ({"name": "Graham", "type": "network"},
                    {"name": "Peter", "type": "network"},
                    {"name": "Mikaela", "type": "network"},
                    {"name": "Toby", "type": "network"},
                    {"name": "Rebecca", "type": "network"},
                    {"name": "Alicia", "type": "network"})
    })

    teams = Team("team_one", ("Graham", "Peter", "Mikaela"), 0), Team("team_one", ("Toby", "Rebecca", "Alicia"), 0)

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        assert player.player_type == NETWORK_PLAYER


def test_computer_player_setup():
    player_info = ({
        "players": ({"name": "Graham", "type": "computer"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = Team("team_one", ("Graham", "Peter", "Mikaela"), 0), Team("team_one", ("Toby", "Rebecca", "Alicia"), 0)

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        assert player.player_type == COMPUTER_PLAYER


def test_player_setup_invalid_type_raises_exception():
    player_info = ({
        "players": ({"name": "Graham", "type": "invalid"},
                    {"name": "Peter", "type": "computer"},
                    {"name": "Mikaela", "type": "computer"},
                    {"name": "Toby", "type": "computer"},
                    {"name": "Rebecca", "type": "computer"},
                    {"name": "Alicia", "type": "computer"})
    })

    teams = Team("team_one", ("Graham", "Peter", "Mikaela"), 0), Team("team_one", ("Toby", "Rebecca", "Alicia"), 0)

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

    teams = Team("team_one", ("Graham", "Peter", "Mikaela"), 0), Team("team_one", ("Toby", "Rebecca", "Alicia"), 0)

    players = game_builder.setup_players(player_info, teams)

    for player in players:
        if player.name in teams[0].player_names:
            assert player.opposing_team == ("Toby", "Rebecca", "Alicia")
        elif player.name in teams[1].player_names:
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

    teams = Team("team_one", ("Graham", "Peter", "Mikaela"), 0), Team("team_one", ("Toby", "Rebecca", "Alicia"), 0)

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

    assert set(teams[0].player_names).isdisjoint(teams[1].player_names)
    assert len(teams[0].player_names) == 3
    assert len(teams[1].player_names) == 3
