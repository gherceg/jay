from app.data.game_enums import CardSet


def test_low_spades():
    assert CardSet.LOW_SPADES.value == ('2s', '3s', '4s', '5s', '6s', '7s')


def test_low_clubs():
    assert CardSet.LOW_CLUBS.value == ('2c', '3c', '4c', '5c', '6c', '7c')


def test_low_diamonds():
    assert CardSet.LOW_DIAMONDS.value == ('2d', '3d', '4d', '5d', '6d', '7d')


def test_low_hearts():
    assert CardSet.LOW_HEARTS.value == ('2h', '3h', '4h', '5h', '6h', '7h')


def test_high_spades():
    assert CardSet.HIGH_SPADES.value == ('9s', '10s', 'js', 'qs', 'ks', 'as')


def test_high_clubs():
    assert CardSet.HIGH_CLUBS.value == ('9c', '10c', 'jc', 'qc', 'kc', 'ac')


def test_high_diamonds():
    assert CardSet.HIGH_DIAMONDS.value == ('9d', '10d', 'jd', 'qd', 'kd', 'ad')


def test_high_hearts():
    assert CardSet.HIGH_HEARTS.value == ('9h', '10h', 'jh', 'qh', 'kh', 'ah')
