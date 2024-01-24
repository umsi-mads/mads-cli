from pathlib import Path

from mads.environ import Docker


def test_docker_default(env):
    """Test the default Docker configuration"""

    # Clear all docker env config
    for key in env.keys():
        if key.startswith("DOCKER_"):
            del env[key]

    docker = Docker()

    assert docker.cache_to is None
    assert docker.cache_from is None


def test_docker_buildx(env):
    """Test the Docker configuration detects buildx"""

    env["DOCKER_CONFIG"] = "/tmp/docker"
    docker = Docker()

    # False because it doesn't exist
    assert docker.buildx is False


def test_docker_paths(env):
    """Test the Docker configuration with paths"""

    env.update(
        {
            "DOCKER_CACHE_TO": "/tmp/cache/to",
            "DOCKER_CACHE_FROM": "/tmp/cache/from",
        }
    )
    docker = Docker()

    assert docker.cache_to == Path("/tmp/cache/to")
    assert docker.cache_from == Path("/tmp/cache/from")


def test_docker_urls(env):
    """Test the Docker configuration with URLs"""

    env.update(
        {
            "DOCKER_CACHE_TO": "1234567890.dkr.ecr.us-east-1.amazonaws.com/cache/to",
            "DOCKER_CACHE_FROM": "1234567890.dkr.ecr.us-east-1.amazonaws.com/cache/from",
        }
    )
    docker = Docker()

    assert docker.cache_to == Path(
        "1234567890.dkr.ecr.us-east-1.amazonaws.com/cache/to"
    )
    assert docker.cache_from == Path(
        "1234567890.dkr.ecr.us-east-1.amazonaws.com/cache/from"
    )
