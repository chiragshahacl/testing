from pathlib import Path

from buildtools.utils import constants


class NotAProjectPath(RuntimeError):
    def __init__(self, path: Path):
        super().__init__(f"No `{constants.BUILD_FILE_NAME}` found in `{path}`")
