"""
The argument parser for the CLI -- The entrypoint API
"""

import argparse
from importlib import metadata

from . import commands


parser = argparse.ArgumentParser(
    "mads",
    description="MADS commands",
    epilog="This tool lives at https://github.com/umsi-mads/mads-cli",
)
parser.set_defaults(func=lambda _: parser.print_help())

subcommands = parser.add_subparsers(title="Commands", help="Available commands")


def register_module_as_subcommand(
    name: str, mod, subparser: argparse._SubParsersAction
):
    """Register a module as a subcommand"""

    help = getattr(mod, "__doc__", getattr(mod, "help", None))
    cmd = subparser.add_parser(name, help=help)
    cmd.set_defaults(func=lambda _: cmd.print_help())

    try:
        mod.register_subcommand(cmd)
    except AttributeError:
        pass

    return cmd


# Load all the built in commands
for name in commands.__all__:
    mod = getattr(commands, name)
    register_module_as_subcommand(name, mod, subcommands)

# Look for any plugins via entry points
for entrypoint in metadata.entry_points(group="mads-cli"):
    name = entrypoint.name
    mod = entrypoint.load()
    register_module_as_subcommand(name, mod, subcommands)
