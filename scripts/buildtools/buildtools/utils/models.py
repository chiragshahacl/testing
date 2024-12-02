import os
from dataclasses import dataclass
from pathlib import Path

import toml

from buildtools.utils import errors
from buildtools.utils import constants
from buildtools.utils import git


def get_project_name(path: Path) -> str:
    return path.name.replace("_", "-")


def get_project_category(path: Path) -> str:
    if not path.is_relative_to(git.PATH_TO_REPOSITORY_ROOT):
        raise RuntimeError(f"Path outside project scope: {path}")
    if (
        path.parent.name == constants.SERVICES_FOLDER_NAME
        or path.parent == git.PATH_TO_REPOSITORY_ROOT
    ):
        return path.name
    return get_project_category(path.parent)


@dataclass(eq=True, frozen=True)
class Project:
    name: str
    path: Path
    category: str
    is_deployable: bool

    def has_changes(
        self,
        previous_commit: str,
        current_commit: str,
        libraries_with_changes: set["Project"] | None = None,
    ) -> bool:
        conditions_to_trigger_project_changes = [
            git.path_has_changes(self.path, previous_commit, current_commit)
        ]
        if libraries_with_changes:
            conditions_to_trigger_project_changes.append(
                any(
                    [
                        self.depends_on_library(library)
                        for library in libraries_with_changes
                        if library.path != self.path  # avoid self-references
                    ]
                )
            )
        return any(conditions_to_trigger_project_changes)

    def depends_on_library(self, library: "Project") -> bool:
        try:
            with open(self.path / constants.DEPENDENCIES_FILE_NAME, "r") as file:
                data = toml.load(file)
        except FileNotFoundError:
            return False
        return library.name in data["tool"]["poetry"]["dependencies"].keys()

    @property
    def is_library(self) -> bool:
        return self.category == constants.LIBRARIES_FOLDER_NAME

    @classmethod
    def from_path(cls, path: Path) -> "Project":
        if not os.path.isfile(path / constants.BUILD_FILE_NAME):
            raise errors.NotAProjectPath(path)

        return cls(
            name=get_project_name(path),
            path=path,
            category=get_project_category(path),
            is_deployable=os.path.isdir(path / constants.DEPLOY_FOLDER),
        )


@dataclass
class BuildMatrix:
    include: set[Project]
