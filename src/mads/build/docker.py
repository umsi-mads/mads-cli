"""
Helpers for interacting with Docker.
"""

import os
import base64
import boto3
from mads.environ import Git, CodeBuild
from .shell import proc


def host() -> str:
    """
    Return the hostname of the Docker host.
    """

    if os.environ.get("IMAGE_HOST"):
        return os.environ["IMAGE_HOST"]

    codebuild = CodeBuild()
    return f"{codebuild.account_id}.dkr.ecr.{codebuild.region}.amazonaws.com"


def start() -> bool:
    """
    Start the Docker daemon.
    """

    # If docker is already running, we're good.
    result = proc("docker info")
    if result.returncode == 0:
        return True

    result = proc("/usr/local/bin/dockerd-entrypoint.sh")
    return result.returncode == 0


def login() -> bool:
    """
    Log into the Docker registry.
    """

    ecr = boto3.client("ecr")
    token = ecr.get_authorization_token()
    user, passwd = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode("utf-8")
        .split(":")
    )

    result = proc(f"docker login -u {user} --password-stdin {host()}", input=passwd)
    return result.returncode == 0


def try_pull(image_name: str, tag: str) -> bool:
    """
    Pull the tagged docker image if it exists. If it doesn't, pull the latest
    version and re-tag it instead.
    """

    result = proc(f"docker pull {image_name}:{tag}")
    if result.returncode == 0:
        return True

    result = proc(f"docker pull {image_name}:latest")
    if result.returncode != 0:
        raise RuntimeError("It appears the requested image doesn't exist at all.")

    result = proc(f"docker tag {image_name}:latest {image_name}{tag}")
    if result.returncode != 0:
        raise RuntimeError(f"Unable to tag the latest image as :{tag}")

    return True


def determine_tag(*, use_branch: bool = False, default: str = "dev") -> str:
    """
    Use the git status to determine the tag we should be using
    """

    git = Git()

    if not git.branch:
        return default

    if use_branch:
        return git.branch

    if git.branch in ["master", "main"]:
        return "latest"

    if git.branch in ["beta"]:
        return "beta"

    else:
        return default
