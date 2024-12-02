from github import Github, Auth
from buildtools.settings import settings


class GithubClient:
    def __init__(self):
        if not all([settings.GITHUB_TOKEN, settings.GITHUB_REPOSITORY]):
            raise ValueError("Missing envs variables")

        self.client = Github(auth=Auth.Token(settings.GITHUB_TOKEN))
        self.repository = self.client.get_repo(settings.GITHUB_REPOSITORY)

    def get_last_successful_commit(self) -> str | None:
        workflows = self.repository.get_workflows()

        if workflows.totalCount == 0:
            print("No workflow found")
            return None

        workflow = next(
            (wf for wf in workflows if wf.name == settings.WORKFLOW_NAME), None
        )

        if not workflow:
            print(f"Workflow with {settings.WORKFLOW_NAME} not found")
            return None

        successful_runs = workflow.get_runs(status="success")

        if successful_runs.totalCount == 0:
            print("No successful runs found")
            return None

        return successful_runs[0].head_sha
