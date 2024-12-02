from pathlib import Path
from typing import Optional
import typer
from loguru import logger

from buildtools.utils import monorepo, git, interface
from buildtools.utils.github import GithubClient
import os

app = typer.Typer()


GET_PROJECTS_HELP = """
output-location: Where to place generated output file
previous_commit: Optional[str] = None,
current-commit: Commit to compare with base commit
category: Filter by project category
deployable: Filter by whether a project is deployable or not
"""

GET_LAST_SUCCESSFUL_COMMIT = """
"""


@app.command(help=GET_PROJECTS_HELP)
def get_projects(
    output_location: Path,
    previous_commit: Optional[str] = None,
    current_commit: Optional[str] = None,
    category: Optional[str] = None,
    deployable: Optional[bool] = None,
):
    projects = monorepo.get_projects(git.PATH_TO_REPOSITORY_ROOT)
    if previous_commit is not None and current_commit is not None:
        libraries_with_changes = {
            project
            for project in projects
            if project.is_library
            and project.has_changes(previous_commit, current_commit)
        }

        libraries_with_dependency_changes = {
            project
            for project in projects
            if project.is_library
            and project.has_changes(
                previous_commit, current_commit, libraries_with_changes
            )
        }
        projects = {
            project
            for project in projects
            if not project.is_library
            and project.has_changes(
                previous_commit, current_commit, libraries_with_changes
            )
        }

        projects = projects | libraries_with_changes | libraries_with_dependency_changes

    if deployable is not None:
        projects = {
            project for project in projects if project.is_deployable == deployable
        }

    if category is not None:
        projects = {project for project in projects if project.category == category}

    result = interface.export_for_build_matrix(projects, output_location)
    logger.debug(result)


@app.command(help=GET_PROJECTS_HELP)
def get_last_successful_commit():
    hash_value = GithubClient().get_last_successful_commit()
    print(f"found last successful commit {hash_value}")

    if not hash_value:
        print("Could not find any successful workflow")
        return

    with open(os.environ["GITHUB_OUTPUT"], "a") as github_output:
        print(
            f"COMMIT_HASH={hash_value}",
            file=github_output,
        )


@app.command()
def ignore():
    pass
