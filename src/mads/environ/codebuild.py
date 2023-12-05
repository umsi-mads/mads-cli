"""Information about the Codebuild environment."""

from typing import Union

from pydantic import BaseSettings, validator


class CodeBuild(BaseSettings):
    """Information provided by Codebuild."""

    initiator: str = ""
    build_id: str = ""
    build_arn: str = ""
    source_version: str = ""
    webhook_event: str = ""
    webhook_head_ref: str = ""
    webhook_base_ref: str = ""

    class Config:
        """Change behavior of the codebuild config class"""

        # When loading in values from the environment, they will all be prefixed
        env_prefix = "codebuild_"

    @property
    def account_id(self) -> str:
        """Return the account ID from the build ARN"""
        return self.build_arn.split(":")[4]

    @property
    def region(self) -> str:
        """Return the region from the build ARN"""
        return self.build_arn.split(":")[3]

    @property
    def base(self) -> str:
        """Return just the name of the base ref"""
        return self.webhook_base_ref.replace("refs/heads/", "")

    @property
    def head(self) -> str:
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

        if self.head and self.base:
            return f"{self.head} -> {self.base}"

        if self.head:
            return self.head

        return None

    @validator("base", check_fields=False)
    def must_come_from_dev(cls, base, values):
        """Reject pull requests that we don't allow."""

        if base in ["master", "main"] and values["head"] != "dev":
            raise RuntimeError()
