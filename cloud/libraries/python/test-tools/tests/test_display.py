from test_tools.display import dict_diff


def test_dict_diff():
    actual_payload = {
        "name": "John",
        "age": 30,
        "city": "New York",
    }

    expected_payload = {
        "name": "Alice",
        "city": "San Francisco",
        "country": "USA",
    }

    result = dict_diff(actual_payload, expected_payload, padding=15, sort_keys=True)

    assert isinstance(result, str) and len(result) > 0


def test_dict_diff_os_error(mocker):
    mocker.patch("os.get_terminal_size", side_effect=OSError)

    actual_payload = {
        "name": "John",
        "age": 30,
        "city": "New York",
    }

    expected_payload = {
        "name": "Alice",
        "city": "San Francisco",
        "country": "USA",
    }

    result = dict_diff(actual_payload, expected_payload, padding=15, sort_keys=True)

    assert isinstance(result, str) and len(result) > 0
