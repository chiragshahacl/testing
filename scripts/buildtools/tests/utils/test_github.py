from buildtools.settings import settings
from buildtools.utils.github import GithubClient
import pytest


@pytest.fixture()
def github_client(mocker):
    return mocker.patch("buildtools.utils.github.Github")


@pytest.fixture()
def github_token(mocker):
    return mocker.patch("buildtools.utils.github.Auth.Token")


def test_github_client_initialization(github_client, github_token):
    instance = GithubClient()

    assert instance.client == github_client.return_value
    github_client.return_value.get_repo.assert_called_once_with(
        settings.GITHUB_REPOSITORY
    )
    github_token.assert_called_once_with("github_token")


def test_last_successful_commit_missing_workflows(mocker, github_client):
    instance = GithubClient()
    instance.repository.get_workflows.return_value = mocker.Mock(totalCount=0)

    assert instance.get_last_successful_commit() is None


def test_last_successful_commit_invalid_workflow_name(mocker, github_client):
    instance = GithubClient()
    workflow = mocker.Mock(name="foo")
    instance.repository.get_workflows.return_value = mocker.MagicMock(
        totalCount=1, side_effect=workflow
    )

    assert instance.get_last_successful_commit() is None


class MockIterator:
    """
    Mock of `github.PaginatedList`
    """

    def __init__(self, workflows):
        self.workflows = workflows
        self.totalCount = len(workflows)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.workflows):
            workflow = self.workflows[self.index]
            self.index += 1
            return workflow
        raise StopIteration

    def __getitem__(self, index):
        return self.workflows[index]


def test_last_successful_filters_by_success(mocker, github_client):
    instance = GithubClient()
    workflow = mocker.Mock()
    workflow.name = settings.WORKFLOW_NAME
    instance.repository.get_workflows.return_value = MockIterator([workflow])
    workflow.get_runs.return_value = MockIterator([])

    instance.get_last_successful_commit()

    workflow.get_runs.assert_called_once_with(status="success")


def test_last_successful_missing_runs(mocker, github_client):
    instance = GithubClient()
    workflow = mocker.Mock()
    workflow.name = settings.WORKFLOW_NAME
    instance.repository.get_workflows.return_value = MockIterator([workflow])
    workflow.get_runs.return_value = MockIterator([])

    assert instance.get_last_successful_commit() is None


def test_last_successful_returns_sha(mocker, github_client):
    instance = GithubClient()
    workflow = mocker.Mock()
    workflow.name = settings.WORKFLOW_NAME
    instance.repository.get_workflows.return_value = MockIterator([workflow])
    workflow.get_runs.return_value = MockIterator([mocker.Mock(head_sha="abc123")])

    assert instance.get_last_successful_commit() == "abc123"
