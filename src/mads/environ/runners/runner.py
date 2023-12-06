"""
Support for multiple runner environments.

For example, we could be running in a GitHub Action, a CodeBuild Build, or outside of a
CI runner entirely.
"""

from abc import ABC, abstractmethod
from pydantic import BaseSettings, validator


class Runner(BaseSettings, ABC):
    """
    A Runner should tell us details about why this operation is running by pulling
    information from the environment.
    """

    # Which runner service are we running in?
    name: str

    # Which repository are we working in?
    repo: str

    # What is the ID of the run?
    run_id: str

    # What branch/commit are we running on?
    ref: str

    # What even triggered this run?
    event: str | None = None

    # If this is a PR, what refs are we working with?
    head_ref: str | None = None
    base_ref: str | None = None

    _runners = []

    # Save a list of all subclasses so we can detect which one we're running in
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        Runner._runners.append(cls)

    @classmethod
    def current(cls):
        """Return an instance of the current runner"""
        for runner in cls._runners:
            if runner.detect():
                return runner
        raise RuntimeError("Unable to detect runner")

    @classmethod
    @abstractmethod
    def detect(cls) -> bool:
        """Detect if we're running in this class of runner"""

    @validator("repo", "head_ref", "base_ref", pre=True)
    def must_be_name_only(cls, v: str) -> str | None:
        """These fields should be the name only, not a URL-like format"""

        if not v:
            return None
        return v.split("/")[-1].replace(".git", "")
