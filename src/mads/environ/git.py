"""Determine information about the current git commit."""

import os
from pathlib import Path
from subprocess import CalledProcessError
from functools import cache

from pydantic import BaseSettings, Field

from mads.build.shell import shell


def determine_branch(commit: str, cwd: Path) -> str:
    """There are a lot of whacky ways to determine the current branch."""

    if "GITHUB_REF_NAME":
        return os.environ["GITHUB_REF_NAME"]

    if "CODEBUILD_WEBHOOK_HEAD_REF" in os.environ:
        return os.environ["CODEBUILD_WEBHOOK_HEAD_REF"].replace("refs/heads/", "")

    if "refs/heads/" in commit:
        return commit.split("refs/heads/")[-1]

    try:
        # The name of the file which contains the commit hash is the branch name
        # that we want. This may be insufficient if the commit we're building isn't
        # technically the HEAD of the branch.
        return (
            shell(
                f"grep --files-with-matches -r {commit}",
                cwd=cwd.joinpath("refs/heads"),
            )
            .split("\n")[0]
            .replace("./", "")
        )
    except (CalledProcessError, FileNotFoundError):
        if commit:
            return commit[:7]
        else:
            return "unknown"


@cache
def git_config_source() -> dict[str, str]:
    cwd = Path(".git")

    # If the git cache is populated, .git is actually a file pointing to the
    # real directory.
    if cwd.is_file():
        realpath = cwd.read_text(encoding="utf-8").split(": ")[1]
        cwd = Path(realpath)

    if not cwd.exists():
        return {
            "commit": "",
            "message": "[This does not appear to be a git project]",
            "branch": "",
            "author": "",
        }

    config = {}

    # The environment should always contain the commit hash that AWS checked out
    config["commit"] = os.environ.get(
        "CODEBUILD_RESOLVED_SOURCE_VERSION",
        os.environ.get("GITHUB_SHA", ""),
    )

    try:
        # If that's not available, ask git for it
        if not config["commit"]:
            config["commit"] = shell("git show -s --format=%h")
    except CalledProcessError:
        pass

    try:
        # If that's not available, we can try to get it from the git cache
        if not config["commit"]:
            config["commit"] = (
                cwd.joinpath("HEAD").read_text().strip().split(":")[-1].strip()
            )
    except FileNotFoundError:
        pass

    try:
        # Given a commit hash, it should always be easy to get the contents
        data = shell(f"git show -s --format='%s;;;%ae' {config['commit']}")
        config["message"], config["author"] = data.split(";;;")
    except (CalledProcessError, KeyError, ValueError):
        pass

    try:
        config["branch"] = determine_branch(config["commit"], cwd)
    except (CalledProcessError, KeyError):
        pass

    return config


class Git(BaseSettings):
    """Load information about git"""

    commit: str | None = Field(..., env="CODEBUILD_RESOLVED_SOURCE_VERSION")
    message: str | None = Field("[unable to retrieve commit message]")
    author: str | None
    branch: str | None

    class Config:
        @classmethod
        def customise_sources(cls, *args, **kwargs):
            return [lambda x: git_config_source()]
