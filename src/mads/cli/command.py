"""Helper for creating CLI commands with typed arguments"""

import os
import sys
import argparse
from functools import wraps
import inspect
from types import UnionType
import typing
from enum import Enum


def die(msg, code=1):
    """Print a message and exit with a non-zero status code."""

    print(msg, file=sys.stderr)
    sys.exit(code)


def set_output(**values):
    """GitHub Actions output helper"""

    outfile = os.environ.get("GITHUB_OUTPUT", sys.stderr.fileno())
    with open(outfile, "a") as f:
        f.write("\n".join([f"{key}={value}" for key, value in values.items()]))


def kebab(str) -> str:
    """Convert a string to kebab-case"""
    return str.replace("_", "-")


def has_parent_type(subject, parent):
    """Check if a class has a parent class"""

    if parent in getattr(subject, "__bases__", []):
        return subject

    if isinstance(subject, UnionType):
        return next(has_parent_type(subtype, parent) for subtype in subject.__args__)

    return None


class Argspec:
    """Create a type to hold arguments to pass along to subparser.add_argument"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            "Argspec[" + ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items()) + "]"
        )


def parse_annotated_metadata(metadata) -> dict[str, typing.Any]:
    """Parse metadata from an annotation"""

    meta = {}

    for md in metadata:
        if isinstance(md, Argspec):
            meta.update(md.__dict__)

    return meta


def parse_type_annotation(name: str, annotation: type) -> dict[str, typing.Any]:
    hints = {}

    # If the annotation is a union, it doesn't make sense to specify a type.
    if not isinstance(annotation, UnionType):
        hints["type"] = annotation

    if isinstance(annotation, typing._AnnotatedAlias):
        hints["type"] = annotation.__origin__
        hints.update(parse_annotated_metadata(annotation.__metadata__))

    hints["dest"] = hints.pop("name", name)

    # If the type is a bool, set the action to store_true
    if hints.get("type", annotation) == bool:
        hints["default"] = hints.get("default", False)
        hints["action"] = "store_false" if hints["default"] else "store_true"

        # If using store_true or store_false, a type is not allowed
        hints.pop("type", None)

    if enum := has_parent_type(annotation, Enum):
        # If the annotation is an Enum, set the choices to the enum values
        hints["choices"] = [e.value for e in enum]

    return hints


def command(subparsers: argparse._SubParsersAction):
    """
    Decorator to register a function as a command

    The function's annotations will be used to create the command's arguments.
    """

    def parse_annotations(func) -> argparse.ArgumentParser:
        """Decorator to register a function as a command"""

        # The subparser we're generating
        sub = subparsers.add_parser(kebab(func.__name__), help=func.__doc__)

        # First, read the annotations and use them to generate arguments
        spec = inspect.getfullargspec(func)

        # Apply the parsed arguments as keyword arguments to the function
        @wraps(func)
        def wrapper(args: argparse.Namespace):
            callargs = []
            for name, val in args._get_kwargs():
                if name == "func":
                    continue
                if spec.varargs == name:
                    callargs.extend(val)
                else:
                    callargs.append(val)
            try:
                return func(*callargs)
            except ValueError as e:
                print(e, file=sys.stderr)
                sub.print_help()
                return

        # Add the function as a subcommand
        sub.set_defaults(func=wrapper)

        # Get a mapping from arg name to default value
        defaults = {}
        if spec.defaults:
            defaults = dict(zip(spec.args[-len(spec.defaults) :], spec.defaults))

        def process_arg(arg, is_vararg=False):
            if arg in ["self", "args"]:
                return

            parserargs = {}

            if arg in defaults:
                parserargs["default"] = defaults[arg]

            if is_vararg:
                parserargs["nargs"] = "*"

            annotation: type = spec.annotations.get(arg)

            is_union = isinstance(annotation, typing._UnionGenericAlias)

            if annotation:
                parserargs.update(parse_type_annotation(arg, annotation))

            # If "no input" is allowed, make this arg a flag
            if arg in defaults or is_union and type(None) in annotation.__args__:
                parserargs["dest"] = f"--{parserargs['dest']}"

            sub.add_argument(parserargs.pop("dest"), **parserargs)

        for arg in spec.args:
            try:
                process_arg(arg)
            except Exception as e:
                print(f"Error processing argument {arg}: {e}", file=sys.stderr)

        if spec.varargs:
            try:
                process_arg(spec.varargs, True)
            except Exception as e:
                print(f"Error processing vararg {spec.varargs}: {e}", file=sys.stderr)

        return sub

    return parse_annotations
