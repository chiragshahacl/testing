import tempfile
from pathlib import Path

import orjson

from buildtools.utils import interface
from buildtools.utils.interface import custom_encode, export_for_build_matrix
from buildtools.utils.models import Project


def test_custom_encode_path():
    result = interface.custom_encode(Path("/hello/world"))

    assert result == "/hello/world"


def test_custom_encode_set():
    result = interface.custom_encode({1, 2, 3})

    assert result == [1, 2, 3]


def test_export_for_build_matrix(mocker):
    expected_projects = {
        mocker.MagicMock(spec=Project),
        mocker.MagicMock(spec=Project),
    }
    output_location = Path("/tmp/hello/world")
    matrix_class_mock = mocker.patch("buildtools.utils.interface.BuildMatrix")
    dumps_mock = mocker.patch.object(orjson, "dumps")
    write_to_file_mock = mocker.patch("buildtools.utils.interface.write_to_file")

    result = export_for_build_matrix(expected_projects, output_location)

    matrix_class_mock.assert_called_once_with(include=expected_projects)
    dumps_mock.assert_called_once_with(
        matrix_class_mock.return_value,
        default=custom_encode,
    )
    write_to_file_mock.assert_called_once_with(dumps_mock.return_value, output_location)
    assert result == dumps_mock.return_value
