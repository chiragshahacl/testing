from pathlib import Path

import orjson

from buildtools.utils.models import Project, BuildMatrix


def custom_encode(obj):
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def write_to_file(data: bytes, file_path: Path) -> None:
    with open(file_path, "wb") as file:
        file.write(data)


def export_for_build_matrix(projects: set[Project], output_location: Path) -> bytes:
    matrix = BuildMatrix(include=projects)
    data = orjson.dumps(matrix, default=custom_encode)
    write_to_file(data, output_location)
    return data
