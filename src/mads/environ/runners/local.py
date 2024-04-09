import time
from pydantic import Field


from mads.lib.path import current_repo
from .runner import Runner


class LocalRunner(Runner):
    """We're running locally, not in a CI environment."""

    name: str = "local"
    repo: str = Field(default_factory=current_repo)
    run_id: str = Field(default_factory=lambda: str(int(time.time())))
    ref: str = "HEAD"

    @classmethod
    def detect(cls) -> bool:
        """Detect if we're running in this class of runner"""

        return True
