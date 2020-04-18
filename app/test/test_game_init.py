from pandas import DataFrame

from app import game_builder
from app.data import Team
from app.constants import *
import app.game_state as game_state


def test_network_player_setup():
    player_info = ({
        "players": ({"name": "p1", "type": "network", "team": "t1"},
                    {"name": "p2", "type": "network", "team": "t1"},
                    {"name": "p3", "type": "network", "team": "t1"},
                    {"name": "p4", "type": "network", "team": "t2"},
                    {"name": "p5", "type": "network", "team": "t2"},
                    {"name": "p6", "type": "network", "team": "t2"})
    })

    teams = Team("t1", ("p1", "p2", "p3"), 0), Team("t2", ("p4", "p5", "p6"), 0)

    state = game_state.create_default_state(("p1", "p2", "p3", "p4", "p5", "p6"))
    players = game_builder.setup_players(player_info, teams, state)

    for player in players:
        assert player.player_type == NETWORK_PLAYER


def test_computer_player_setup():
    player_info = ({
        "players": ({"name": "p1", "type": "computer", "team": "t1"},
                    {"name": "p2", "type": "computer", "team": "t1"},
                    {"name": "p3", "type": "computer", "team": "t1"},
                    {"name": "p4", "type": "computer", "team": "t2"},
                    {"name": "p5", "type": "computer", "team": "t2"},
                    {"name": "p6", "type": "computer", "team": "t2"})
    })

    teams = Team("t1", ("p1", "p2", "p3"), 0), Team("t2", ("p4", "p5", "p6"), 0)

    state = game_state.create_default_state(("p1", "p2", "p3", "p4", "p5", "p6"))
    players = game_builder.setup_players(player_info, teams, state)

    for player in players:
        assert player.player_type == COMPUTER_PLAYER


def test_player_setup_invalid_type_raises_exception():
    player_info = ({
        "players": ({"name": "p1", "type": "computer", "team": "t1"},
                    {"name": "p2", "type": "computer", "team": "t1"},
                    {"name": "p3", "type": "computer", "team": "t1"},
                    {"name": "p4", "type": "computer", "team": "t2"},
                    {"name": "p5", "type": "computer", "team": "t2"},
                    {"name": "p6", "type": "computer", "team": "t2"})
    })

    teams = Team("t1", ("p1", "p2", "p3"), 0), Team("t2", ("p4", "p5", "p6"), 0)

    state = game_state.create_default_state(("p1", "p2", "p3", "p4", "p5", "p6"))
    try:
        players = game_builder.setup_players(player_info, teams, state)
    except ValueError:
        assert True
    else:
        assert False


def test_opposing_teams():
    player_info = ({
        "players": ({"name": "p1", "type": "computer", "team": "t1"},
                    {"name": "p2", "type": "computer", "team": "t1"},
                    {"name": "p3", "type": "computer", "team": "t1"},
                    {"name": "p4", "type": "computer", "team": "t2"},
                    {"name": "p5", "type": "computer", "team": "t2"},
                    {"name": "p6", "type": "computer", "team": "t2"})
    })

    teams = Team("t1", ("p1", "p2", "p3"), 0), Team("t2", ("p4", "p5", "p6"), 0)

    state = game_state.create_default_state(("p1", "p2", "p3", "p4", "p5", "p6"))
    players = game_builder.setup_players(player_info, teams, state)

    for player in players:
        if player.name in teams[0].player_names:
            assert player.opponents == ("p4", "p5", "p6")
        elif player.name in teams[1].player_names:
            assert player.opponents == ("p1", "p2", "p3")
        else:
            assert False


def test_teammates():
    player_info = ({
        "players": ({"name": "p1", "type": "computer", "team": "t1"},
                    {"name": "p2", "type": "computer", "team": "t1"},
                    {"name": "p3", "type": "computer", "team": "t1"},
                    {"name": "p4", "type": "computer", "team": "t2"},
                    {"name": "p5", "type": "computer", "team": "t2"},
                    {"name": "p6", "type": "computer", "team": "t2"})
    })

    teams = Team("t1", ("p1", "p2", "p3"), 0), Team("t2", ("p4", "p5", "p6"), 0)

    state = game_state.create_default_state(("p1", "p2", "p3", "p4", "p5", "p6"))
    players = game_builder.setup_players(player_info, teams, state)

    for player in players:
        if player.name == "p1":
            assert player.teammates == ("p2", "p3")
        elif player.name == "p4":
            assert player.teammates == ("p5", "p6")


def test_setup_teams():
    settings = ({
        "players": ({"name": "p1", "type": "computer"},
                    {"name": "p2", "type": "computer"},
                    {"name": "p3", "type": "computer"},
                    {"name": "p4", "type": "computer"},
                    {"name": "p5", "type": "computer"},
                    {"name": "p6", "type": "computer"})
    })

    teams = game_builder.setup_teams(settings)

    assert set(teams[0].player_names).isdisjoint(teams[1].player_names)
    assert len(teams[0].player_names) == 3
    assert len(teams[1].player_names) == 3
