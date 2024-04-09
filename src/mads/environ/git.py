"""Determine information about the current git commit."""

from pathlib import Path
from subprocess import CalledProcessError
from functools import cache

from pydantic_settings import BaseSettings

from mads.build.shell import shell

NOT_GIT = {"message": "[This does not appear to be a git project]"}


@cache
def git_config_source() -> dict[str, str]:
    cwd = Path(".git")

    # If the git cache is populated, .git is actually a file pointing to the
    # real directory.
    if cwd.is_file():
        realpath = cwd.read_text(encoding="utf-8").split(": ")[1]
        cwd = Path(realpath)

    if not cwd.exists():
        return NOT_GIT

    head = cwd.joinpath("HEAD")

    if not head.exists():
        return NOT_GIT

    config = {}

    headref = head.read_text().strip()

    if "ref: " in headref:
        config["branch"] = headref.split("refs/heads/")[-1]

        config["commit"] = cwd.joinpath(headref.split(" ")[1]).read_text().strip()[:7]
    else:
        config["branch"] = "HEAD"

        config["commit"] = headref[:7]

    try:
        # Given a commit hash, it should always be easy to get the contents
        data = shell(f"git show -s --format='%s;;;%ae' {config['commit']}")
        config["message"], config["author"] = data.split(";;;")
    except (CalledProcessError, KeyError, ValueError):
        pass

    return config


class Git(BaseSettings):
    """Load information about git"""

    commit: str | None = None
    message: str | None = None
    author: str | None = None
    branch: str | None = None

    @classmethod
    def settings_customise_sources(cls, *args, **kwargs) -> tuple:
        return (git_config_source,)
