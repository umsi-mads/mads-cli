"""Dump the loaded environment"""

import argparse
from functools import partial
from rich.pretty import pprint

from mads import environ


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the environ command"""

    def run(args):
        """Run the query"""

        p = partial(pprint, indent_guides=False, expand_all=True)
        p(environ.Git())
        p(environ.Docker())
        p(environ.Runner.current())
        p(environ.Resources())
        p(environ.InOut())

    parser.set_defaults(func=run)
