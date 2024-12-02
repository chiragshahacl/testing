from os import terminal_size

import pytest
from test_tools.asserts import assert_contains, assert_deep_equal, common_items


@pytest.fixture(autouse=True)
def mock_terminal_size(mocker):
    mocker.patch("os.get_terminal_size", return_value=terminal_size([100, 100]))


def test_common_items():
    actual = {
        "key1": {
            "nested_key1_1": "nested_value1_1_actual",
            "nested_key1_2": "nested_value1_2_actual",
        },
        "key2": {
            "nested_key2_1": "nested_value2_1_actual",
            "nested_key2_2": "nested_value2_2_actual",
        },
    }
    expected = {"key1": {"nested_key1_1": "nested_value1_1_expected"}}

    result = common_items(actual, expected)

    assert result == {"key1": {"nested_key1_1": "nested_value1_1_actual"}}


@pytest.mark.parametrize(
    "some_dict",
    [
        {},
        {"foo": "bar"},
        {"foo": 5},
        {"foo": ["b", "a", "r"]},
        {"foo": {"bar": "baz"}},
        {"foo": {"bar": "baz", "qux": [1, 2, 3]}},
    ],
)
def test_deep_equal_equal_dicts(some_dict):
    try:
        assert_deep_equal(some_dict, some_dict)
    except AssertionError:
        pytest.fail("Equal dict comparison shouldn't fail")


@pytest.mark.parametrize(
    "actual, expected, message",
    [
        ({"foo": "bar"}, {}, "Item root['foo'] removed from dictionary"),
        ({}, {"foo": "bar"}, "Item root['foo'] added to dictionary"),
        (
            {"foo": "bar"},
            {"foo": "baz"},
            'Value of root[\'foo\'] changed from "bar" to "baz"',
        ),
        (
            {"foo": {"bar": "bar"}},
            {"foo": {"bar": "baz"}},
            "Value of root['foo']['bar'] changed from \"bar\" to \"baz\"",
        ),
        (
            {"foo": [1, 2, 3]},
            {"foo": [1, 2]},
            "Item root['foo'][2] removed from iterable",
        ),
    ],
)
def test_deep_equal_different_dicts(actual, expected, message):
    with pytest.raises(AssertionError) as exc_info:
        assert_deep_equal(actual, expected)

    assert message in exc_info.value.args[0]


@pytest.mark.parametrize(
    "actual, expected, messages",
    [
        (
            {"foo": "bar", "baz": "qux"},
            {},
            [
                "Item root['foo'] removed from dictionary",
                "Item root['baz'] removed from dictionary",
            ],
        ),
        (
            {"foo": "bar", "baz": [1, 2, 3]},
            {"foo": "baz", "baz": [1, 2]},
            [
                'Value of root[\'foo\'] changed from "bar" to "baz"',
                "Item root['baz'][2] removed from iterable",
            ],
        ),
    ],
)
def test_deep_equal_multiple_differences_dicts(actual, expected, messages):
    with pytest.raises(AssertionError) as exc_info:
        assert_deep_equal(actual, expected)

    for message in messages:
        assert message in exc_info.value.args[0]


@pytest.mark.parametrize(
    "actual, expected",
    [
        ({}, {}),
        ({"foo": "bar", "baz": "qux"}, {"foo": "bar"}),
        ({"foo": {"bar": "baz"}, "qux": "quux"}, {"foo": {"bar": "baz"}}),
        ({"foo": [1, 2, 3], "qux": "quux"}, {"foo": [1, 2, 3]}),
    ],
)
def test_assert_contains_valid_dicts(actual, expected):
    try:
        assert_contains(actual, expected)
    except AssertionError:
        pytest.fail("Contained dict comparison shouldn't fail")


@pytest.mark.parametrize(
    "actual, expected",
    [
        ([], []),
        (["foo", "bar"], ["foo", "bar"]),
    ],
)
def test_assert_contains_valid_lists(actual, expected):
    try:
        assert_contains(actual, expected)
    except AssertionError:
        pytest.fail("Contained dict comparison shouldn't fail")


@pytest.mark.parametrize(
    "actual, expected, message",
    [
        ({"qux": "waldo"}, {"foo": "bar"}, "Item root['foo'] added to dictionary"),
        (
            {"foo": "bar", "qux": "waldo"},
            {"foo": "baz"},
            'Value of root[\'foo\'] changed from "bar" to "baz"',
        ),
        (
            {"foo": {"bar": "bar"}, "qux": "waldo"},
            {"foo": {"bar": "baz"}},
            "Value of root['foo']['bar'] changed from \"bar\" to \"baz\"",
        ),
        (
            {"foo": [1, 2, 3], "qux": "waldo"},
            {"foo": [1, 2]},
            "Item root['foo'][2] removed from iterable",
        ),
    ],
)
def test_assert_contains_invalid_dicts(actual, expected, message):
    # this tests assumes there's a key 'qux' in the actual dict
    # but not in the expected dict, to prove this is only comparing
    # the keys the dicts have in common
    assert "qux" in actual
    assert "qux" not in expected

    with pytest.raises(AssertionError) as exc_info:
        assert_contains(actual, expected)

    exc_message = exc_info.value.args[0]

    assert message in exc_message
    assert "qux" not in exc_message, "there shouldn't be a mention of the extra key"


@pytest.mark.parametrize(
    "actual, expected, message",
    [
        (["foo"], ["foo", "bar"], "Item root[1] added to iterable"),
        (["foo", "bar"], ["foo"], "Item root[1] removed from iterable"),
    ],
)
def test_assert_contains_invalid_lists(actual, expected, message):
    with pytest.raises(AssertionError) as exc_info:
        assert_contains(actual, expected)

    exc_message = exc_info.value.args[0]

    assert message in exc_message
