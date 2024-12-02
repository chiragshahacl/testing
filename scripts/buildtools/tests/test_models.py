import pytest
from tests.factories.model_factory import ServiceProjectFactory, LibraryProjectFactory


@pytest.mark.parametrize("has_changes", [True, False])
def test_project_has_changes_without_dependencies(mocker, has_changes):
    service_project = ServiceProjectFactory()
    mocker.patch("buildtools.utils.git.path_has_changes", return_value=has_changes)

    assert service_project.has_changes("commit1", "commit2") is has_changes


@pytest.mark.parametrize("has_changes", [True, False])
def test_lib_has_changes_with_lib_dependencies_with_changes(
    mocker, tmpdir, has_changes
):
    mocker.patch("buildtools.utils.git.path_has_changes", return_value=has_changes)

    lib1 = LibraryProjectFactory(path=tmpdir / "lib1")
    lib2 = LibraryProjectFactory()
    lib1.add_dependency(lib2)

    assert lib1.has_changes("commit1", "commit2", {lib2}) is True


def test_lib_dont_have_changes_with_itself_as_dependencies(mocker, tmpdir):
    """
    Having itself as dependency is not something possible, but it doesn't hurt to avoid it
    """

    mocker.patch("buildtools.utils.git.path_has_changes", return_value=False)
    lib = LibraryProjectFactory(path=tmpdir / "lib2")
    lib.add_dependency(lib)

    assert lib.has_changes("commit1", "commit2", {lib}) is False
