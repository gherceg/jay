from app.util.Optional import Optional


# Tests for Optional.empty()
def test_optional_empty_creates_empty():
    test_optional = Optional.empty()
    assert test_optional.value == None


# Tests for Optional.isEmpty()
def test_optional_is_empty_is_true():
    test_optional = Optional(None)
    expected = True
    actual = test_optional.isEmpty()
    assert expected == actual


def test_optional_is_empty_is_false():
    test_optional = Optional("something")
    expected = False
    actual = test_optional.isEmpty()
    assert expected == actual


# Tests for Optional.isPresent()
def test_optional_is_present_is_true():
    test_optional = Optional("something")
    expected = True
    actual = test_optional.isPresent()
    assert expected == actual


def test_optional_is_present_is_false():
    test_optional = Optional(None)
    expected = False
    actual = test_optional.isPresent()
    assert expected == actual


# Tests for Optional.get()
def test_optional_get_succeeds():
    expected = "something"
    test_optional = Optional(expected)
    assert expected == test_optional.get()


def test_optional_get_throws_exception():
    expected = None
    test_optional = Optional.empty()
    try:
        test_optional.get()
    except ValueError:
        assert True
        return
    else:
        assert False
