"""Helpers for setting up a build environment"""

from mads.cli.command import command
import argparse


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the setup command"""

    setupcmd = parser.add_subparsers(title="Setup commands", help="Available commands")

    @command(setupcmd)
    def install(repo_name: str, branch: str = "main"):
        """Private python package install"""

        from mads.build import shell

        url = f"git+https://github.com/umsi-mads/{repo_name}.git@{branch}"
        shell(f"pip install {url}")
