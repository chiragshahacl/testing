import os
from pathlib import Path

from buildtools.utils import constants, git
from buildtools.utils.models import Project

IGNORED_PROJECT_DIRECTORIES = [
    git.PATH_TO_REPOSITORY_ROOT / constants.TEMPLATES_FOLDER,
    git.PATH_TO_REPOSITORY_ROOT / constants.INFRA_FOLDER,
]


def get_projects(directory: Path) -> set[Project]:
    build_paths = set()

    for root, dirs, files in os.walk(directory):
        if constants.BUILD_FILE_NAME in files:
            build_path = Path(root)
            should_ignore_path = False
            for ignored_path in IGNORED_PROJECT_DIRECTORIES:
                if build_path.is_relative_to(ignored_path):
                    should_ignore_path = True
                    break
            if not should_ignore_path:
                build_paths.add(Path(root))
            # Stop searching deeper in this directory
            del dirs[:]

    projects = {Project.from_path(p) for p in build_paths}
    return projects
