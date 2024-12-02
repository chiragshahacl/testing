from deepdiff import DeepDiff
from termcolor import colored

from test_tools.display import dict_diff


def assert_deep_equal(actual, expected, sort_keys=True):
    """
    Compares anything* deeply. If the objects are different,
    Raises assertion error with a human readeable message and a diff table.

    The objects to be compared must be JSON encodeable

    * Dicts, Iterables, strings, almost anything.
        See DeepDiff for a full list.
    """
    difference = DeepDiff(actual, expected)
    diff_message = colored(difference.pretty(), "red")

    assert not difference, (
        "\n" + dict_diff(actual, expected, sort_keys=sort_keys) + "\n" + diff_message
    )


def common_items(actual, expected):
    """
    Returns the dict resulting of the intersection between 'actual' and 'expected'.
    The values in this dict will be from the actual.
    This is used to check for a deep comparison of two dicts only in the keys
    they have in common
    Will be called recursively.
    """
    return {
        k: common_items(actual[k], expected[k]) if isinstance(actual[k], dict) else actual[k]
        for k in actual.keys() & expected.keys()
    }


def assert_contains(actual, expected):
    """
    Compares two dicts *only* in the keys they have in common.
    If the dicts are different,
    If they arguments are not dicts, the comparison is done directly
    Raises assertion error with a human readeable message.
    """
    if isinstance(actual, dict) and isinstance(expected, dict):
        actual = common_items(actual, expected)
    assert_deep_equal(actual, expected)
