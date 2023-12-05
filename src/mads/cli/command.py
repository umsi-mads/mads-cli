"""Helper for creating CLI commands with typed arguments"""

import sys
import argparse
from functools import wraps
import inspect
from types import UnionType
from enum import Enum


def die(msg, code=1):
    """Print a message and exit with a non-zero status code."""

    print(msg, file=sys.stderr)
    sys.exit(code)


def kebab(str) -> str:
    """Convert a string to kebab-case"""
    return str.replace("_", "-")


def command(subparsers: argparse._SubParsersAction):
    """
    Decorator to register a function as a command

    The function's annotations will be used to create the command's arguments.
    """

    def parse_annotations(func) -> argparse.ArgumentParser:
        """Decorator to register a function as a command"""

        # Apply the parsed arguments as keyword arguments to the function
        @wraps(func)
        def wrapper(args: argparse.Namespace):
            callargs = dict(args._get_kwargs())
            del callargs["func"]
            return func(**callargs)

        # Add the function as a subcommand
        sub = subparsers.add_parser(kebab(func.__name__), help=func.__doc__)
        sub.set_defaults(func=wrapper)

        # Now, read the annotations and use them to generate arguments
        spec = inspect.getfullargspec(func)

        # Get a mapping from arg name to default value
        defaults = {}
        if spec.defaults:
            defaults = dict(zip(spec.args[-len(spec.defaults) :], spec.defaults))

        for arg in spec.args:
            if arg in ["self", "args"]:
                continue

            parserargs = {}

            if arg in defaults:
                parserargs["default"] = defaults[arg]

            annotation = spec.annotations.get(arg)

            if annotation:
                # If the annotation is a union, it doesn't make sense to specify a type.
                if not isinstance(annotation, UnionType):
                    parserargs["type"] = annotation

                # If "no input" is allowed, make this arg a flag
                if isinstance(None, annotation) or arg in defaults:
                    parserargs["dest"] = f"--{kebab(arg)}"
                else:
                    parserargs["dest"] = arg

                # If the type is a bool, set the action to store_true
                if annotation == bool:
                    parserargs["default"] = parserargs.get("default", False)
                    parserargs["action"] = (
                        "store_false" if parserargs["default"] else "store_true"
                    )

                    # If using store_true or store_false, a type is not allowed
                    parserargs.pop("type", None)

                if Enum in getattr(annotation, "__bases__", []):
                    parserargs["choices"] = [e.value for e in annotation]

            sub.add_argument(parserargs.pop("dest"), **parserargs)
        return sub

    return parse_annotations
