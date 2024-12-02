import subprocess
from pathlib import Path


def _run_command(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True).stdout.decode("utf-8")
    return result.strip()


def _get_repo_root() -> Path:
    git_command = ["git", "rev-parse", "--show-toplevel"]
    return Path(_run_command(git_command))


def get_changed_files(previous_commit: str, current_commit: str) -> list[Path]:
    git_command = ["git", "diff", "--name-only", previous_commit, current_commit]
    changed_files = _run_command(git_command).split("\n")
    return [Path(file.strip()) for file in changed_files]


def path_has_changes(path: Path, previous_commit: str, current_commit: str) -> bool:
    git_command = [
        "git",
        "diff",
        "--name-only",
        previous_commit,
        current_commit,
        "--",
        str(path),
    ]
    changed_files = [
        file_name.strip()
        for file_name in _run_command(git_command).split("\n")
        if file_name
    ]
    return bool(changed_files)


PATH_TO_REPOSITORY_ROOT: Path = _get_repo_root()
