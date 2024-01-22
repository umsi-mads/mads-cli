from pathlib import Path
from pydantic import BaseSettings


class Docker(BaseSettings):
    cache_to: Path | None
    cache_from: Path | None

    class Config:
        env_prefix = "DOCKER_"
