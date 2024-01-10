"""
The CLI interface for MADS builds.
"""

import sys
from argparse import Namespace

from .args import parser

runtime = Namespace(
    verbose=False,
    output=None,
)


def main(argv=sys.argv[1:]):
    """The CLI interface for MADS builds"""

    parsed = parser.parse_args(argv)

    if hasattr(parsed, "verbose"):
        runtime.verbose = parsed.__dict__.pop("verbose")

    if hasattr(parsed, "output"):
        runtime.output = parsed.__dict__.pop("output")

    parsed.func(parsed)
