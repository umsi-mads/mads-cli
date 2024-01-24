import os
from pathlib import Path
from pydantic import BaseSettings, Field


def config_dir():
    """Path to the docker config directory"""
    return Path(os.environ.get("DOCKER_CONFIG", "~/.docker")).expanduser()


class Docker(BaseSettings):
    # Are we using buildkit buildx?
    buildx: bool = Field(
        default_factory=lambda: config_dir()
        .joinpath("cli-plugins/docker-buildx")
        .exists()
    )

    # Environment config
    cache_to: Path | None
    cache_from: Path | None

    class Config:
        env_prefix = "DOCKER_"
