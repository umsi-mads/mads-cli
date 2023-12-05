"""Information about the GitHub Actions environment."""

from typing import Union

from pydantic import BaseSettings, validator


class GitHub(BaseSettings):
    """Information provided by GitHub."""

    actions: bool = False
    run_id: str = ""
    actor: str = ""
    base_ref: str = ""
    head_ref: str = ""
    event_name: str = ""
    ref_name: str = ""
    repository: str = ""
    repository_owner: str = ""

    class Config:
        """Change behavior of the github config class"""

        # When loading in values from the environment, they will all be prefixed
        env_prefix = "github_"
