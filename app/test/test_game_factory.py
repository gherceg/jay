from app.game.GameFactory import GameFactory
from app.test.mocks.MockNetworkDelegate import MockNetworkDelegate

mock_network_delegate = MockNetworkDelegate()


def test_game_factory_create():
    settings = mock_game_settings(True, True)
    game = GameFactory.create_game(mock_network_delegate, settings)
    assert len(game.players) == 6


def test_game_factory_create_no_cards():
    settings = mock_game_settings(False, True)
    game = GameFactory.create_game(mock_network_delegate, settings)
    for (key, player) in game.players.items():
        assert not player.get_cards()


def test_game_factory_setup_teams_specified():
    settings = mock_game_settings(True, True)
    teams = GameFactory.setup_teams(settings)
    assert len(teams) == 2
    assert teams[0]["name"] == "test_team_one"
    assert teams[1]["name"] == "test_team_two"
    assert len(teams[0]["players"]) == 3
    assert len(teams[1]["players"]) == 3
    assert teams[0]["players"] == ["graham", "peter", "mikaela"]
    assert teams[1]["players"] == ["comp1", "comp2", "comp3"]


def test_game_factory_setup_teams_unspecified():
    settings = mock_game_settings(True, False)
    teams = GameFactory.setup_teams(settings)

    assert len(teams) == 2
    assert teams[0]["name"] == "Team 1"
    assert teams[1]["name"] == "Team 2"
    assert len(teams[0]["players"]) == 3
    assert len(teams[1]["players"]) == 3


def mock_game_settings(virtual_deck: bool, include_teams: bool) -> dict:
    settings = {}
    settings["players"] = [
        {"name": "graham", "type": "network"},
        {"name": "peter", "type": "network"},
        {"name": "mikaela", "type": "network"},
        {"name": "comp1", "type": "computer"},
        {"name": "comp2", "type": "computer"},
        {"name": "comp3", "type": "computer"},
    ]

    settings["virtual_deck"] = virtual_deck
    if include_teams:
        settings["teams"] = [
            {"name": "test_team_one", "players": ["graham", "peter", "mikaela"]},
            {"name": "test_team_two", "players": ["comp1", "comp2", "comp3"]}
        ]

    return settings
