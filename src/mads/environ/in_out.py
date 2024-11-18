import sys
import logging
from typing import Any
from pydantic import computed_field, field_validator
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
    shlvl: int | None = None
    log_level: int = logging.INFO

    @field_validator("log_level", mode="before")
    def validate_log_level(cls, v: Any):

        if isinstance(v, str):
            if v.isnumeric():
                v = int(v)
            else:
                v = logging.getLevelName(v)

        return v

    @computed_field
    def is_terminal(self) -> bool:
        if self.force_terminal is not None:
            return self.force_terminal
        return bool(self.is_atty or self.is_subshell)

    @computed_field
    def is_atty(self) -> bool:
        return sys.stdout.isatty()

    @computed_field
    def is_subshell(self) -> bool:
        return self.shlvl is not None and self.shlvl > 1

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
        yield "is_subshell", self.is_subshell
        yield "is_interactive", self.is_interactive
        yield "log_level", logging.getLevelName(self.log_level)

    @classmethod
    def settings_customise_sources(cls, *args, env_settings, **kwargs) -> tuple:
        return (
            runner_settings,
            env_settings,
        )
