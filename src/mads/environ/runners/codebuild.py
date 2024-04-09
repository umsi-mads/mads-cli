"""Information about the Codebuild environment."""

import os
from typing import Union

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .runner import Runner


class CodeBuild(Runner):
    """Information provided by Codebuild."""

    model_config = SettingsConfigDict(env_prefix="codebuild_")

    # Required fields that differ from parent class
    name: str = "codebuild"
    repo: str = Field(alias="codebuild_source_repo_url")
    run_id: str = Field(alias="codebuild_build_id")
    ref: str = Field(alias="codebuild_source_version")

    # Optional fields that differ from parent class
    initiator: str = ""
    build_id: str = ""
    build_arn: str = ""
    source_version: str = ""
    webhook_event: str = ""
    webhook_head_ref: str = ""
    webhook_base_ref: str = ""

    @classmethod
    def detect(cls) -> bool:
        """Detect if we're running in Codebuild"""

        return "CODEBUILD_BUILD_ID" in os.environ

    @property
    def account_id(self) -> str:
        """Return the account ID from the build ARN"""
        return self.build_arn.split(":")[4]

    @property
    def region(self) -> str:
        """Return the region from the build ARN"""
        return self.build_arn.split(":")[3]

    @property
    def base_ref(self) -> str:
        """Return just the name of the base ref"""
        return self.webhook_base_ref.replace("refs/heads/", "")

    @property
    def head_ref(self) -> str:
        """Return just the name of the head ref"""
        return self.webhook_head_ref.replace("refs/heads/", "")

    @property
    def event(self) -> str:
        """Get a colloquial name for the webhook event."""

        if self.webhook_event in ["PUSH", "PULL_REQUEST_UPDATED"]:
            return "update"

        if self.webhook_event in ["PULL_REQUEST_MERGED"]:
            return "merge"

        if "PULL_REQUEST" in self.webhook_event:
            return "PR"

        return "manual"

    @property
    def branch(self) -> Union[str, None]:
        """Get the current git branch."""

        if self.head_ref and self.base_ref:
            return f"{self.head_ref} -> {self.base_ref}"

        if self.head_ref:
            return self.head_ref

        return None
