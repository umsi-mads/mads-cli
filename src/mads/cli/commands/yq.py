"""YAML Query"""

import sys
import argparse
from typing import Any
from functools import reduce
from mads.cli.command import die


def dotget(item: Any, key: str) -> Any | None:
    """
    Return the value of the supplied key from the supplied dict.
    Supports nested keys using dot notation.
    """
    keys = key.split(".")
    return reduce(
        lambda current, next_key: (
            current.get(next_key, None)
            if hasattr(current, "get")
            else getattr(current, str(next_key), None)
        ),
        keys,
        item,
    )


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the setup command"""

    parser.add_argument("query", help="The query to run")
    parser.add_argument("input", help="The file or stream to run it on")
    parser.add_argument("--raw", "-r", help="Output the raw value", action="store_true")

    def run(args):
        """Run the query"""

        from ruamel.yaml import YAML

        yaml = YAML(typ="safe")

        data = {}

        if args.input == "-":
            data = yaml.load(sys.stdin)

        else:
            with open(args.input) as f:
                data = yaml.load(f)

        value = dotget(data, args.query)
        if value is None:
            die(f"The query {args.query!r} returned a None value")

        if args.raw:
            print(value)
        else:
            print(f"{value!r}")

    parser.set_defaults(func=run)
