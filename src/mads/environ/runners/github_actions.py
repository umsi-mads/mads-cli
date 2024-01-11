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
    run_attempt: int = 1

    @classmethod
    def detect(cls) -> bool:
        """Detect if we're running in GitHub Actions"""

        return "GITHUB_ACTIONS" in os.environ

    @property
    def url(self) -> str:
        """The GitHub Actions URL"""

        return (
            f"https://github.com/{self.repository}/actions/runs"
            f"/{self.run_id}/attempts/{self.run_attempt}"
        )

    class Config:
        """Change behavior of the github config class"""

        # When loading in values from the environment, they will all be prefixed
        env_prefix = "github_"
