"""Helpers for interacting with Docker"""

import argparse
from mads.cli.command import command, die, set_output


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the docker command"""

    dockercmd = parser.add_subparsers(
        title="Docker commands", help="Available commands"
    )

    @command(dockercmd)
    def start():
        """Ensure the daemon is running and log in"""

        from mads.build import docker

        if docker.start():
            print("Docker started successfully")
        else:
            die("Unable to start Docker")
        if docker.login():
            print("Logged in successfully")
        else:
            die("Unable to log in")

    @command(dockercmd)
    def try_pull(image_name: str, tag: str):
        """Pull a docker image or the latest if that tag doesn't exist"""

        from mads.build import docker

        docker.try_pull(image_name, tag)

    @command(dockercmd)
    def pull_first(image_name: str, *tags: str):
        """Pull the first available image from the list"""

        from mads.build import docker

        result = docker.pull_first(image_name, *tags)
        if result:
            set_output(pulled=result)

    @command(dockercmd)
    def tag(use_branch: bool = False, default: str = "dev"):
        """Determine what tag to use for the current build"""

        from mads.build import docker

        tag = docker.determine_tag(use_branch=use_branch, default=default)
        print(tag)
