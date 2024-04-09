import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def config_dir():
    """Path to the docker config directory"""
    return Path(os.environ.get("DOCKER_CONFIG", "~/.docker")).expanduser()


class Docker(BaseSettings):
    """Detect how we should interact with Docker."""

    model_config = SettingsConfigDict(env_prefix="docker_")

    # Are we using buildkit buildx?
    buildx: bool = Field(
        default_factory=lambda: config_dir()
        .joinpath("cli-plugins/docker-buildx")
        .exists()
    )

    # Environment config
    cache_to: Path | None = None
    cache_from: Path | None = None
