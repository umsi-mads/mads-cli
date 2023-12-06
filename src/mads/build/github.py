"""
Submit GitHub status checks.
"""

import os
import jwt
import time
from functools import cache
from enum import Enum
from typing import Tuple
from pathlib import Path

from ruamel.yaml import YAML
from ghapi.all import GhApi
import boto3

from .logging import log
from .shell import shell

STATUS_MESSAGES = {
    "pending": "⏳ Build started for project {}",
    "success": "✅ Build succeeded for project {}",
    "failure": "❌ Build failed for project {}",
    "error": "⚠️ Build errored for project {}",
}


class CheckState(str, Enum):
    """The state of a GitHub check."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    FINISHED = "finished"


secrets = boto3.client("secretsmanager")


@cache
def aws_private_key(secret_id: str) -> Tuple[int, int, str]:
    """Load the GitHub private key from secrets manager."""

    secret = secrets.get_secret_value(SecretId=secret_id)
    data = YAML(typ="safe").load(secret["SecretString"])
    return (
        data["app_id"],
        data["installation_id"],
        data["private_key"].encode("utf-8"),
    )


def token(
    app_id: int | None = None,
    installation_id: int | None = None,
    private_key: str | None = None,
    secret_id: str | None = None,
) -> str:
    """Generate an installation token for the GitHub app."""

    if secret_id:
        app_id, installation_id, private_key = aws_private_key(secret_id)

    here = locals()
    missing = [
        key for key in ["app_id", "installation_id", "private_key"] if not here[key]
    ]
    assert len(missing) == 0, f"Missing GitHub app credentials: {missing}"

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id,
    }

    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
    token_client = GhApi(jwt_token=jwt_token)
    response = token_client.apps.create_installation_access_token(installation_id)
    log.info(
        "Created GitHub access token. Will expire in 10 minutes at %s",
        response["expires_at"],
    )
    return response["token"]


def client():
    """Initialize a GitHub API client."""

    return GhApi(token=token())


def install(token: str):
    """Install a github token as a native git credential."""

    creds = Path.home().joinpath(".git-credentials")

    with open(creds, "a") as f:
        f.write(f"https://x-access-token:{token}@github.com\n")

    shell(f"git config --global credential.helper store")

    log.warning("Installed GitHub token to ~/.git-credentials")


def create_status(
    status: str,
    context: str | None = None,
    description: str | None = None,
):
    """Create a status check on GitHub."""

    commit = os.environ["CODEBUILD_RESOLVED_SOURCE_VERSION"]
    org = os.environ["CODEBUILD_SOURCE_REPO_URL"].split("/")[-2]
    repo = os.environ["CODEBUILD_SOURCE_REPO_URL"].split("/")[-1].split(".")[0]

    if status == "finished":
        status = (
            "success" if os.environ["CODEBUILD_BUILD_SUCCEEDING"] == "1" else "failure"
        )

    assert status in STATUS_MESSAGES

    if not context:
        context = "Build"

    if not description:
        description = STATUS_MESSAGES[status].format(repo)

    url = os.environ["CODEBUILD_BUILD_URL"]

    response = client().repos.create_commit_status(
        context=context,
        description=description,
        owner=org,
        repo=repo,
        sha=commit,
        state=status,
        target_url=url,
    )

    if "id" in response:
        log.info(
            "Successfully created commit status: [%s] %s -- %s",
            context,
            status,
            description,
        )
    else:
        log.error(
            "Failed to create commit status: [%s] %s -- %s",
            context,
            status,
            description,
        )
        log.error(response)
