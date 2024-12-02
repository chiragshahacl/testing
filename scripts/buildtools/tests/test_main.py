from pathlib import Path
from tests.factories.model_factory import LibraryProjectFactory, ServiceProjectFactory
from unittest.mock import call

from buildtools.main import get_projects, get_last_successful_commit
from buildtools.utils import git, monorepo, interface


def test_get_projects(mocker):
    repo_root_path = "repo"
    expected_projects = {
        mocker.Mock(category="platforms"),
        mocker.Mock(category="any"),
    }
    output_location = Path("/tmp/expected/location")
    mocker.patch.object(git, "PATH_TO_REPOSITORY_ROOT", repo_root_path)
    get_projects_mock = mocker.patch.object(
        monorepo, "get_projects", return_value=expected_projects
    )
    export_for_build_matrix_mock = mocker.patch.object(
        interface, "export_for_build_matrix"
    )

    get_projects(output_location=output_location)

    get_projects_mock.assert_called_once_with(repo_root_path)
    export_for_build_matrix_mock.assert_called_once_with(
        expected_projects, output_location
    )


def test_get_projects_with_category(mocker):
    repo_root_path = "repo"
    expected_match = mocker.Mock(category="any")
    expected_projects = {
        mocker.Mock(category="platforms"),
        expected_match,
    }
    output_location = Path("/tmp/expected/location")
    mocker.patch.object(git, "PATH_TO_REPOSITORY_ROOT", repo_root_path)
    get_projects_mock = mocker.patch.object(
        monorepo, "get_projects", return_value=expected_projects
    )
    export_for_build_matrix_mock = mocker.patch.object(
        interface, "export_for_build_matrix"
    )

    get_projects(output_location=output_location, category="any")

    get_projects_mock.assert_called_once_with(repo_root_path)
    export_for_build_matrix_mock.assert_called_once_with(
        {expected_match}, output_location
    )


def test_get_deployable_projects(mocker):
    repo_root_path = "repo"
    deployable_project = mocker.Mock(category="platforms", is_deployable=True)
    non_deployable_project = mocker.Mock(category="any", is_deployable=False)
    expected_projects = {
        deployable_project,
        non_deployable_project,
    }
    output_location = Path("/tmp/expected/location")
    mocker.patch.object(git, "PATH_TO_REPOSITORY_ROOT", repo_root_path)
    get_projects_mock = mocker.patch.object(
        monorepo, "get_projects", return_value=expected_projects
    )
    export_for_build_matrix_mock = mocker.patch.object(
        interface, "export_for_build_matrix"
    )

    get_projects(output_location=output_location, deployable=True)

    get_projects_mock.assert_called_once_with(repo_root_path)
    export_for_build_matrix_mock.assert_called_once_with(
        {deployable_project}, output_location
    )


def test_get_projects_with_changes(mocker):
    previous_commit = "commit-1"
    current_commit = "commit-2"
    repo_root_path = "repo"
    projects_without_changes = mocker.Mock(category="platforms")
    projects_without_changes.has_changes.return_value = False
    project_with_changes = mocker.Mock(is_library=False)
    project_with_changes.has_changes.return_value = True
    library_project = mocker.Mock(is_library=True)
    all_projects = {
        library_project,
        projects_without_changes,
        project_with_changes,
    }
    output_location = Path("/tmp/expected/location")
    mocker.patch.object(git, "PATH_TO_REPOSITORY_ROOT", repo_root_path)
    get_projects_mock = mocker.patch.object(
        monorepo, "get_projects", return_value=all_projects
    )
    export_for_build_matrix_mock = mocker.patch.object(
        interface, "export_for_build_matrix"
    )
    expected_projects = set(all_projects)
    expected_projects.remove(projects_without_changes)

    get_projects(output_location, previous_commit, current_commit)

    get_projects_mock.assert_called_once_with(repo_root_path)
    library_project.has_changes.assert_has_calls(
        [
            call(previous_commit, current_commit),
            call(previous_commit, current_commit, {library_project}),
        ]
    )
    project_with_changes.has_changes.assert_called_once_with(
        previous_commit, current_commit, {library_project}
    )

    export_for_build_matrix_mock.assert_called_once_with(
        expected_projects, output_location
    )


def test_get_projects_with_libraries_with_dependencies(mocker, tmpdir):
    """
    lib1 has no changes and depends on lib2
    lib2 has changes
    """

    lib1 = LibraryProjectFactory(path=tmpdir / "lib1")
    lib2 = LibraryProjectFactory(path=tmpdir / "lib2")
    lib1.add_dependency(lib2)
    projects = {lib1, lib2}
    export_for_build_matrix = mocker.patch.object(interface, "export_for_build_matrix")

    def path_has_changes(path, *args):
        # Mocks git.has_changes to only have changes on lib2
        return path == lib2.path

    mocker.patch("buildtools.utils.git.path_has_changes", path_has_changes)
    mocker.patch("buildtools.main.monorepo.get_projects", return_value=projects)

    get_projects(tmpdir / "output", "commit1", "commit2")

    export_for_build_matrix.assert_called_once_with({lib1, lib2}, tmpdir / "output")


def test_get_projects_with_libraries_no_changes_with_dependencies(mocker, tmpdir):
    """
    lib1 has no changes and depends on lib2
    lib2 has no changes
    """

    lib1 = LibraryProjectFactory(path=tmpdir / "lib1")
    lib2 = LibraryProjectFactory(path=tmpdir / "lib2")
    lib1.add_dependency(lib2)
    projects = {lib1, lib2}
    export_for_build_matrix = mocker.patch.object(interface, "export_for_build_matrix")

    mocker.patch("buildtools.utils.git.path_has_changes", return_value=False)
    mocker.patch("buildtools.main.monorepo.get_projects", return_value=projects)

    get_projects(tmpdir / "output", "commit1", "commit2")

    export_for_build_matrix.assert_called_once_with(set(), tmpdir / "output")


def test_get_projects_with_multiple_projects(mocker, tmpdir):
    """
    lib1 has no changes and depends on lib2
    lib2 has changes
    serv1 has no changes but depends on lib1
    serv2 has changes
    serv3 no changes and no dependencies
    """

    lib1 = LibraryProjectFactory(path=tmpdir / "lib1")
    lib2 = LibraryProjectFactory(path=tmpdir / "lib2")
    serv1 = ServiceProjectFactory(path=tmpdir / "serv1")
    serv2 = ServiceProjectFactory(path=tmpdir / "serv2")
    serv3 = ServiceProjectFactory(path=tmpdir / "serv3")
    lib1.add_dependency(lib2)
    serv1.add_dependency(lib1)

    def path_has_changes(path, *args):
        # Mocks git.has_changes to only have changes on lib2
        return path in [lib2.path, serv1.path, serv2.path]

    projects = {lib1, lib2, serv1, serv2, serv3}
    export_for_build_matrix = mocker.patch.object(interface, "export_for_build_matrix")

    mocker.patch("buildtools.utils.git.path_has_changes", path_has_changes)
    mocker.patch("buildtools.main.monorepo.get_projects", return_value=projects)

    get_projects(tmpdir / "output", "commit1", "commit2")

    export_for_build_matrix.assert_called_once_with(
        {lib1, lib2, serv1, serv2}, tmpdir / "output"
    )


def test_get_last_successful_commit_not_found(mocker, tmpdir, monkeypatch):
    github_client = mocker.patch("buildtools.main.GithubClient")
    get_hash = github_client.return_value.get_last_successful_commit
    get_hash.return_value = None
    github_output = tmpdir / "github.output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(github_output))

    get_last_successful_commit()

    assert not github_output.exists()


def test_get_last_successful_found(mocker, tmpdir, monkeypatch):
    github_client = mocker.patch("buildtools.main.GithubClient")
    get_hash = github_client.return_value.get_last_successful_commit
    get_hash.return_value = "abc123"
    github_output = tmpdir / "github.output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(github_output))

    get_last_successful_commit()

    assert github_output.exists()
    with github_output.open() as f:
        assert f.read() == "COMMIT_HASH=abc123\n"
