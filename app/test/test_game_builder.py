from app.gameplay import game_builder


def test_game_factory_create():
    settings = mock_game_settings(True, True)
    game = game_builder.create_game(settings)
    assert len(game.players) == 6


def test_game_factory_create_no_cards():
    settings = mock_game_settings(False, True)
    game = game_builder.create_game(settings)
    for (key, player) in game.players.items():
        assert not player.get_cards()


def test_game_factory_setup_teams_specified():
    settings = mock_game_settings(True, True)
    teams = game_builder.setup_teams(settings)
    assert len(teams) == 2
    assert teams[0].name == "t1"
    assert teams[1].name == "t2"
    assert len(teams[0].player_names) == 3
    assert len(teams[1].player_names) == 3
    assert teams[0].player_names == ["p1", "p2", "p3"]
    assert teams[1].player_names == ["comp1", "comp2", "comp3"]


def test_game_factory_setup_teams_unspecified():
    settings = mock_game_settings(True, False)
    teams = game_builder.setup_teams(settings)

    assert len(teams) == 2
    assert teams[0].name == "Team 1"
    assert teams[1].name == "Team 2"
    assert len(teams[0].player_names) == 3
    assert len(teams[1].player_names) == 3


def mock_game_settings(virtual_deck: bool, include_teams: bool) -> dict:
    settings = {}
    settings["players"] = [
        {"name": "p1", "type": "network", "team": "t1"},
        {"name": "p2", "type": "network", "team": "t1"},
        {"name": "p3", "type": "network", "team": "t1"},
        {"name": "comp1", "type": "computer", "team": "t2"},
        {"name": "comp2", "type": "computer", "team": "t2"},
        {"name": "comp3", "type": "computer", "team": "t2"},
    ]

    settings["virtual_deck"] = virtual_deck
    if include_teams:
        settings["teams"] = [
            {"name": "t1", "players": ["p1", "p2", "p3"]},
            {"name": "t2", "players": ["comp1", "comp2", "comp3"]}
        ]

    return settings
