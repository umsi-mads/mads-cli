"""
The argument parser for the CLI -- The entrypoint API
"""

import sys
import argparse
from importlib import metadata

from . import commands


parser = argparse.ArgumentParser(
    "mads",
    description="MADS commands",
    epilog="This tool lives at https://github.com/umsi-mads/mads-cli",
)
parser.add_argument("--verbose", "-v", action="store_true", help="Output more logs")
parser.set_defaults(func=lambda _: parser.print_help())

subcommands = parser.add_subparsers(title="Commands", help="Available commands")


def register_module_as_subcommand(
    name: str, mod, subparser: argparse._SubParsersAction
):
    """Register a module as a subcommand"""

    register = getattr(mod, "register_subcommand", None)

    if register:
        help = (
            getattr(mod, "__doc__", None)
            or getattr(register, "__doc__", None)
            or getattr(mod, "help", None)
            or ""
        )
        cmd = subparser.add_parser(name, help=help)
        cmd.set_defaults(func=lambda _: cmd.print_help())
        try:
            register(cmd)
        except Exception as e:

            def wrap(err):
                def print_warning(_):
                    print(
                        "There was a problem registering this command:\n",
                        err,
                        file=sys.stderr,
                    )

                return print_warning

            cmd.set_defaults(func=wrap(e))

        return cmd

    print(
        f"Command {name} ({mod.__name__}) does not have a register_subcommand function",
        file=sys.stderr,
    )


# Look for any plugins via entry points
for entrypoint in metadata.entry_points(group="mads-cli"):
    name = entrypoint.name

    try:
        mod = entrypoint.load()
        register_module_as_subcommand(name, mod, subcommands)
    except Exception:
        print("Problem importing entrypoint", entrypoint, file=sys.stderr)
        continue

# Load all the built in commands
for name in commands.__all__:
    mod = getattr(commands, name)
    register_module_as_subcommand(name, mod, subcommands)
