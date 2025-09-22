"""Utility functions for external repositories management."""

from pathlib import Path

from git import Repo


def clone_repository(repository_url: str, target_path: Path) -> Repo:
    """Clone a Git repository to a target path.

    Args:
        repository_url: The URL of the repository to clone.
        target_path: The path to clone the repository to.

    Returns:
        Repo: GitPython repository object representing the cloned repository.

    """
    return Repo.clone_from(repository_url, target_path)
