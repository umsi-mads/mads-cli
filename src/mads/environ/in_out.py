import sys
from pydantic import computed_field
from pydantic_settings import BaseSettings
from .runners import Runner


def runner_settings() -> dict:
    """Override the detected settings with runner information"""

    runner = Runner.current
    return runner.io_settings


class InOut(BaseSettings):
    """The input/output we're running with. IO is a reserved name in some contexts."""

    term: str | None = None
    force_terminal: bool | None = None

    @computed_field
    def is_terminal(self) -> bool:
        if self.force_terminal is not None:
            return self.force_terminal
        return self.is_atty

    @computed_field
    def is_atty(self) -> bool:
        return sys.stdout.isatty()

    @computed_field
    def is_interactive(self) -> bool:
        return self.is_atty and not self.is_dumb

    @property
    def is_dumb(self) -> bool:
        return self.term is not None and self.term.lower() in ("dumb", "unknown")

    def __rich_repr__(self):
        yield "term", self.term
        yield "is_terminal", self.is_terminal
        yield "force_terminal", self.force_terminal, None
        yield "is_atty", self.is_atty, True
        yield "is_interactive", self.is_interactive

    @classmethod
    def settings_customise_sources(cls, *args, env_settings, **kwargs) -> tuple:
        return (
            runner_settings,
            env_settings,
        )
