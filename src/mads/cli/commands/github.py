"""Helpers for interacting with GitHub"""

import argparse
from mads.cli.command import command
from mads.build.github import CheckState


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the github command"""

    ghcmd = parser.add_subparsers(title="GitHub commands", help="Available commands")

    @command(ghcmd)
    def token(
        app_id: int | None,
        installation_id: int | None,
        private_key: str | None,
        secret_id: str | None,
        install: bool = False,
    ):
        """Generate a temporary app installation token"""
        from mads.build import github

        token = github.token(
            app_id=app_id,
            installation_id=installation_id,
            private_key=private_key,
            secret_id=secret_id,
        )

        if install:
            github.install(token)

        print(token)

    @command(ghcmd)
    def commit_status(status: CheckState, context: str | None, description: str | None):
        """Create a GitHub commit status for the current commit"""

        from mads.build import github

        github.create_status(status, context, description)
