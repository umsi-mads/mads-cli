"""Helpers for setting up a build environment"""

import sys
from mads.cli.command import command
import argparse


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the setup command"""

    setupcmd = parser.add_subparsers(title="Setup commands", help="Available commands")

    @command(setupcmd)
    def install(repo_name: str, branch: str = "main"):
        """Private python package install"""

        from mads.build import proc

        url = f"git+https://github.com/umsi-mads/{repo_name}.git"
        branch_url = f"{url}@{branch}"
        branch_install = proc(f"pip install --no-cache-dir {branch_url}")

        if branch != "main" and branch_install.returncode != 0:
            print(
                f"Failed to install {repo_name} from branch {branch}, falling back to main",
                file=sys.stderr,
            )
            proc(f"pip install {url}")
