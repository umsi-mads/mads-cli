"""Information about the GitHub Actions environment."""

import os
from pydantic import Field
from .runner import Runner


class GitHubActions(Runner):
    """Information provided by GitHub Actions."""

    # Required fields that differ from parent class
    name: str = "github"
    repo: str = Field(env="github_repository")
    ref: str = Field(env="github_ref_name")
    event: str = Field(env="github_event_name")

    # Optional fields that differ from parent class
    actions: bool = False
    actor: str = ""
    repository: str = ""
    repository_owner: str = ""

    @classmethod
    def detect(cls) -> bool:
        """Detect if we're running in GitHub Actions"""

        return "GITHUB_ACTIONS" in os.environ

    class Config:
        """Change behavior of the github config class"""

        # When loading in values from the environment, they will all be prefixed
        env_prefix = "github_"
