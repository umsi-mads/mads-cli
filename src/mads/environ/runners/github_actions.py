"""Information about the GitHub Actions environment."""

import os
from typing import ClassVar
from pydantic import Field
from .runner import Runner
from pydantic_settings import SettingsConfigDict


class GitHubActions(Runner):
    """Information provided by GitHub Actions."""

    model_config = SettingsConfigDict(env_prefix="github_")

    # Required fields that differ from parent class
    name: str = "github"
    repo: str = Field(..., alias="github_repository")
    ref: str = Field(..., alias="github_ref_name")
    event: str = Field(..., alias="github_event_name")

    # Optional fields that differ from parent class
    actions: bool = False
    actor: str = ""
    repository: str = Field(..., alias="github_repository")
    repository_owner: str = ""
    run_attempt: int = 1

    io_settings: ClassVar[dict] = {"force_terminal": False}

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
